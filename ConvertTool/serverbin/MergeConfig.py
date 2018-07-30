#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#将多个配置json合并成1个

import os
import sys
import re
from optparse import OptionParser 
import json
import time
import collections

#Usage:
#          ./MergeConfig.py -f <from_dir> -t <tofile>
#Example:  ./MergeConfig.py -f ./server/ -t ./server/Config.zip

#输入参数说明：
# -f 待合并的json文件目录
# -t 转换到的目标文件名

def ConvertConfig():
    
    reload(sys)
    sys.setdefaultencoding('utf-8')

    #1.读取命令行参数
    parser = OptionParser() 
    parser.add_option("-f", "--fromdir", action="store", dest="fromdir", help="待合并的json文件目录") 
    parser.add_option("-t", "--tofile", action="store", dest="tofile", help="转换到的目标文件名") 
    (options, args) = parser.parse_args()       

    if options.fromdir is None: 
        parser.error("please input from config dir") 
        return

    if options.tofile is None:
        parser.error("please input convert to file name.")
        return

    fromdir = options.fromdir
    tofilename = options.tofile

    #2.读取所有的配置文件
    jsonData = {}
    for onefile in os.listdir(fromdir):
        if os.path.isfile(os.path.join(fromdir,onefile)) and os.path.splitext(onefile)[1] == ".json":
            jsonData[onefile] = json.load(open(os.path.join(fromdir, onefile)))

    #3.保存到文件
    fp = file(tofilename,'w')
    json.dump(jsonData, fp, indent=2)
    
    print "\n"

    print "Success to merge %s config file!\n"%(fromdir)

if __name__ == '__main__':
    ConvertConfig()