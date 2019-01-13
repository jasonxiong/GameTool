#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#将多个配置json合并成1个Json配置或Lua配置

import os
import sys
import re
from optparse import OptionParser 
import json
import time
import collections
import types
import string

#Usage:
#          ./MergeConfig.py -f <from_dir> -t <tofile>
#Example:  ./MergeConfig.py -f ./server/ -t ./server/Config.zip

#输入参数说明：
# -f 待合并的json文件目录
# -t 转换到的目标文件名

LUA_CONFIG_TEMPLATE_FILE = "server_lua/ConfigTemplate.lua"

def SpaceStr(layer):
    	lua_str = ""
	for i in range(0, layer):
		lua_str += '\t'
	return lua_str

 # json转换成lua table，返回lua table串，可能会返回空
def JsonToLuaStr(data, layer=0):    
    if isinstance(data,types.StringTypes) or isinstance(data,str) or isinstance(data,types.UnicodeType):
		return "'" + data + "'"
    elif isinstance(data,types.BooleanType):
		if data:
			return 'true'
		else:
			return 'false'
    elif isinstance(data,types.IntType) or isinstance(data,types.LongType) or isinstance(data,types.FloatType):
		return str(data)
    elif isinstance(data,types.ListType):
        lua_str = "{\n"
        lua_str += SpaceStr(layer+1)
        for i in range(0,len(data)): 
            lua_str += JsonToLuaStr(data[i],layer+1)
            if i < len(data)-1:
                lua_str += ','
        lua_str += '\n'
        lua_str += SpaceStr(layer)
        lua_str +=  '}'
        return lua_str
    elif isinstance(data,types.DictType) or isinstance(data, types.DictionaryType):
        lua_str = ''
        lua_str += "\n"
        lua_str += SpaceStr(layer)
        lua_str += "{\n"
        data_len = len(data)
        data_count = 0
        for k,v in data.items():
            data_count += 1
            lua_str += SpaceStr(layer+1)
            if type(k) is types.IntType:
                lua_str += '[' + str(k) + ']'
            else:
                lua_str += k 
            lua_str += ' = '
            try:
                lua_str += JsonToLuaStr(v,layer +1)
                if data_count < data_len:
                    lua_str += ',\n'

            except Exception, e:
                print 'error in ',k,v
                return None
        lua_str += '\n'
        lua_str += SpaceStr(layer)
        lua_str += '}'
        return lua_str
    else:
		print type(data) , 'is error'
		return None

def ConvertConfig():
    
    reload(sys)
    sys.setdefaultencoding('utf-8')

    #1.读取命令行参数
    parser = OptionParser() 
    parser.add_option("-f", "--fromdir", action="store", dest="fromdir", help="待合并的json文件目录和lua文件目录") 
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
            if "Config.zip" in tofilename:
                jsonData[onefile] = json.load(open(os.path.join(fromdir, onefile)))
            elif "server_config.lua" in tofilename:
                jsonData[onefile.replace('.json','')] = json.load(open(os.path.join(fromdir, onefile)))

    #3.保存到文件
    if "Config.zip" in tofilename:
        #转换成zip文件
        fp = file(tofilename,'w')
        json.dump(jsonData, fp, indent=2)
    elif "server_config.lua" in tofilename:
        #转换成lua配置
        fpTemplate = file(LUA_CONFIG_TEMPLATE_FILE,'r')
        fp = file(tofilename, 'w')
        values = {'xdby_config_lua' : JsonToLuaStr(jsonData)}
        fp.write(string.Template(fpTemplate.read()).substitute(values))
    else:
        print "Failed to merge config, invalid to file name %s"%tofilename
    
    print "\n"

    print "Success to merge %s config file!\n"%(fromdir)

if __name__ == '__main__':
    ConvertConfig()