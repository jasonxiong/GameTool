#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#配置转换工具

import os
import sys
import re
from optparse import OptionParser 
import json
import time
import xlwt
import xlrd
import collections
from xml.dom.minidom import Document

#Usage:
#          ./ConvertTool.py -f <from_excel>
#Example:  ./ConvertTool.py -f source.xls

#输入参数说明：
# -f 要转换的配置Excel文件名
# -c 读取的转换规则配置文件名
# -t 转换类型字符串，支持 xml,json和bin 三种格式

def ConvertConfig():
    
    reload(sys)
    sys.setdefaultencoding('utf-8')

    #1.读取命令行参数
    parser = OptionParser() 
    parser.add_option("-f", "--fromfile", action="store", dest="fromfile", help="要转换的Excel文件名") 
    (options, args) = parser.parse_args()       

    if options.fromfile is None: 
        parser.error("please input config excel file.") 
        return

    CONFIG_DIR='config/'
    CLIENT_DIR='client/'
    SERVER_DIR='server/'
    CONFIG_FILE='config.json'

    fromfile = options.fromfile

    #2.读取配置文件
    jsonData = None
    with open(CONFIG_DIR+CONFIG_FILE, 'r') as JsonConfFile:
        jsonData = json.load(JsonConfFile)

    #判断字段是否存在
    if jsonData.get("server") is None or jsonData.get("client") is None:
        print "Invalid config.json, no server or client data!"
        return

    #3.读取Excel文件
    excelData = xlrd.open_workbook(CONFIG_DIR+options.fromfile)
    
    #先生成服务器的
    print "------------------------ServerConfig------------------------"
    iRet = ConvertOneConfig(SERVER_DIR, jsonData["server"]["filelist"], excelData, jsonData["server"]["totype"])
    if iRet != 0:
        print "Failed to config server file, ret %d"%(iRet)
        return
    
    print "\n"

    #再生成客户端的
    print "------------------------ClientConfig------------------------"
    iRet = ConvertOneConfig(CLIENT_DIR, jsonData["client"]["filelist"], excelData, jsonData["client"]["totype"])
    if iRet != 0:
        print "Failed to config client file, ret %d"%(iRet)
        return

    print "\n"

    print "Success to convert all config file!"

def ConvertOneConfig(outDir, jsonData, excelData, tofiletype):
    for convertInfo in jsonData:
        table = excelData.sheet_by_name(convertInfo["fromfile"])
        tofile = outDir+"/"+convertInfo["tofile"]
        fp = file(tofile,'w')
        nColumns = table.ncols

        #先确定所有字段在table中的位置
        dataIndexs = [-1] * len(convertInfo["data"])
        tableRowValues = table.row_values(0)
        for i in range(0, len(convertInfo["data"])):
            if convertInfo["data"][i]["name"] not in tableRowValues:
                #要转换的字段不存在
                print "table %s"%(convertInfo["fromfile"])+" : %s not exist!"%(convertInfo["data"][i]["name"])
                continue
            
            #确定字段在Excel表中的位置
            dataIndexs[i] = tableRowValues.index(convertInfo["data"][i]["name"])

        #保存输出数据
        if tofiletype == "json":
            #转换成json
            outData = []

            #遍历Excel表中的行
            for rowIndex in range(1, table.nrows):
                oneOutData = collections.OrderedDict()
                for i in range(0, len(dataIndexs)):
                    if dataIndexs[i] < 0:
                        #找不到该字段
                        print "Failed to convert %s"%(convertInfo["fromfile"])+", no data %s"%(convertInfo["data"][i]["name"])
                        return -1
                    
                    #写入数据
                    if convertInfo["data"][i]["type"] == "int":
                        # int 类型数据
                        oneOutData[convertInfo["data"][i]["name"]] = int(table.cell(rowIndex, dataIndexs[i]).value)
                    elif convertInfo["data"][i]["type"] == "string":
                        # string 类型数据
                        oneOutData[convertInfo["data"][i]["name"]] = table.cell(rowIndex, dataIndexs[i]).value
                    else:
                        print "not support type %s"%(convertInfo["data"][i]["type"])+",table: %s"%(convertInfo["fromfile"])
                        return -2
                    
                outData.append(oneOutData)

            #输出数据到文件中
            json.dump(outData, fp, indent=2)

        elif tofiletype == "xml":
            #转换成xml
            outData = Document()

            #创建根节点
            rootNode = outData.createElement('root')
            outData.appendChild(rootNode)

            #遍历Excel表中的行
            for rowIndex in range(1, table.nrows):
                
                #创建一个记录
                oneRecordNode = outData.createElement(convertInfo["fromfile"])
                rootNode.appendChild(oneRecordNode)

                for i in range(0, len(dataIndexs)):
                    if dataIndexs[i] < 0:
                        #找不到该字段
                        print "Failed to convert %s"%(convertInfo["fromfile"])+", no data %s"%(convertInfo["data"][i]["name"])
                        return -1
                    
                    #创建一列数据的节点
                    oneData = outData.createElement(convertInfo["data"][i]["name"])
                    
                    #写入数据内容
                    oneDataText = None
                    if convertInfo["data"][i]["type"] == "int":
                        # int 类型数据
                        oneDataText = outData.createTextNode(str(int(table.cell(rowIndex, dataIndexs[i]).value)))
                    elif convertInfo["data"][i]["type"] == "string":
                        # string 类型数据
                        oneDataText = outData.createTextNode(str(table.cell(rowIndex, dataIndexs[i]).value))
                    else:
                        print "not support type %s"%(convertInfo["data"][i]["type"])+",table: %s"%(convertInfo["fromfile"])
                        return -2
                    
                    oneData.appendChild(oneDataText)

                    #插入到记录中
                    oneRecordNode.appendChild(oneData)

            #输出数据到文件中
            with open(tofile, 'w') as f:
                f.write(outData.toprettyxml(indent="\t", encoding='utf-8'))

        elif tofiletype == "bin":
            #转换成二进制 todo jasonxiong
            pass
        else:
            "Failed to convert config, invalid tofiletype %s"%(tofiletype)
            return -2

        print "process excel table success, Table: %s "%(convertInfo["fromfile"])

    return 0

if __name__ == '__main__':
    ConvertConfig()