#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 配置转换工具

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
import types

# Usage:
#          ./ConvertTool.py -f <from_excel> -t <type>
# Example:  ./ConvertTool.py -f source.xls -t client

# 输入参数说明：
# -f 要转换的配置Excel文件名
# -t 转换的配置类型， client 为客户端， server 为服务器


def ConvertConfig():

    reload(sys)
    sys.setdefaultencoding('utf-8')

    # 1.读取命令行参数
    parser = OptionParser()
    parser.add_option("-f", "--fromfile", action="store",
                      dest="fromfile", help="要转换的Excel文件名")
    parser.add_option("-t", "--type", action="store",
                      dest="convtype", help="转换的类型，客户端或服务器或lua")
    (options, args) = parser.parse_args()

    if options.fromfile is None:
        parser.error("please input config excel file.")
        return

    if options.convtype is None:
        parser.error("please input convert type.")
        return

    fromfile = options.fromfile
    convtype = options.convtype

    CONFIG_DIR = 'config/'

    if convtype == "client":
        CONFIG_FILE = 'client.json'
        CONF_TO_DIR = 'client/'
    elif convtype == "server":
        CONFIG_FILE = 'server.json'
        CONF_TO_DIR = 'server/'
    elif convtype == 'server_lua':
        CONFIG_FILE = 'server_lua.json'
        CONF_TO_DIR = 'server_lua/'

    else:
        print("invalid convtype %s\n" % (convtype))
        return

    # 2.读取配置文件
    jsonData = None
    with open(CONFIG_DIR+CONFIG_FILE, 'r') as JsonConfFile:
        jsonData = json.load(JsonConfFile)

    # 3.读取Excel文件
    excelData = xlrd.open_workbook(CONFIG_DIR+options.fromfile)

    # 先生成服务器的
    print "------------------------ConvertConfig------------------------"
    iRet = ConvertOneConfig(
        CONF_TO_DIR, jsonData["filelist"], excelData, jsonData["totype"])
    if iRet != 0:
        print "Failed to convert %s file, ret %d" % (convtype, iRet)
        return

    print "\n"

    '''
    # 再生成客户端的
    print "------------------------ClientConfig------------------------"
    iRet = ConvertOneConfig(
        CLIENT_DIR, jsonData["client"]["filelist"], excelData, jsonData["client"]["totype"])
    if iRet != 0:
        print "Failed to config client file, ret %d"%(iRet)
        return

    print "\n"
    '''

    print "Success to convert %s config file!\n" % (convtype)

def ConvertOneConfig(outDir, jsonData, excelData, tofiletype):
    for convertInfo in jsonData:
        table = excelData.sheet_by_name(convertInfo["fromfile"])
        tofile = outDir+"/"+convertInfo["tofile"]
        fp = file(tofile,'w')
        nColumns = table.ncols

        # 先确定所有字段在table中的位置
        dataIndexs = [-1] * len(convertInfo["data"])
        tableRowValues = table.row_values(0)
        for i in range(0, len(convertInfo["data"])):
            if convertInfo["data"][i]["name"] not in tableRowValues:
                # 要转换的字段不存在
                print "table %s"%(convertInfo["fromfile"])+" : %s not exist!"%(convertInfo["data"][i]["name"])
                continue
            
            # 确定字段在Excel表中的位置
            dataIndexs[i] = tableRowValues.index(convertInfo["data"][i]["name"])

        # 保存输出数据
        if tofiletype == "json":
            # 转换成json
            outData = []

            # 遍历Excel表中的行
            for rowIndex in range(1, table.nrows):
                oneOutData = collections.OrderedDict()
                for i in range(0, len(dataIndexs)):
                    if dataIndexs[i] < 0:
                        # 找不到该字段
                        print "Failed to convert %s"%(convertInfo["fromfile"])+", no data %s"%(convertInfo["data"][i]["name"])
                        return -1
                    
                    # 写入数据
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

            # 输出数据到文件中
            json.dump(outData, fp, indent=2)

        elif tofiletype == "xml":
            # 转换成xml
            outData = Document()

            # 创建根节点
            rootNode = outData.createElement('root')
            outData.appendChild(rootNode)

            # 遍历Excel表中的行
            for rowIndex in range(1, table.nrows):
                
                # 创建一个记录
                oneRecordNode = outData.createElement(convertInfo["fromfile"])
                rootNode.appendChild(oneRecordNode)

                for i in range(0, len(dataIndexs)):
                    if dataIndexs[i] < 0:
                        # 找不到该字段
                        print "Failed to convert %s"%(convertInfo["fromfile"])+", no data %s"%(convertInfo["data"][i]["name"])
                        return -1
                    
                    # 创建一列数据的节点
                    oneData = outData.createElement(convertInfo["data"][i]["name"])
                    
                    # 写入数据内容
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

                    # 插入到记录中
                    oneRecordNode.appendChild(oneData)

            # 输出数据到文件中
            with open(tofile, 'w') as f:
                f.write(outData.toprettyxml(indent="\t", encoding='utf-8'))
                
        elif tofiletype == "bin":
            # 转换成二进制 todo jasonxiong
            pass
        else:
            "Failed to convert config, invalid tofiletype %s"%(tofiletype)
            return -2

        print "process excel table success, Table: %s "%(convertInfo["fromfile"])

    return 0

if __name__ == '__main__':
    ConvertConfig()
