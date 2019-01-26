#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 服务器发版工具

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
from contextlib import closing
import types
import pymysql
import paramiko
import scpclient

# Usage:    ./DeployServer.py

#服务器目录
SERVER_DIR = "server/"

#更新内容配置文件
CONFIG_FILE = "Config.json"

#lua和proto数据库信息
DBHOST = '192.168.135.121'
DBPORT = 3306
DBUSER = 'hello'
DBPASSWD = '8F3V8e_9'
CHARSET= 'utf8mb4'
DBNAME = 'config_public'
LUATABLE = 'LuaFiles'
PROTOTABLE = 'ProtoFiles'

#dbp信息
DBPHOST = '192.168.135.122'
DBPUSER = 'root'
DBPPASSWD = 'Bf~2sd6190123'

#GameSvr信息
GSHOST = '192.168.135.123'
GSUSER = 'root'
GSPASSWD = 'bftest123!@#'

def DeployServer():

    reload(sys)
    sys.setdefaultencoding('utf-8')

    # 1.读取配置文件
    configData = None
    with open(SERVER_DIR+CONFIG_FILE, 'r') as JsonConfFile:
        configData = json.load(JsonConfFile)

    #2.先连接数据库
    conn = pymysql.connect(
        host = DBHOST,
        port = DBPORT,
        user = DBUSER,
        passwd = DBPASSWD,
        db = DBNAME,
        charset = CHARSET
        )

    cursor = conn.cursor()

    # 3.更新proto
    for oneProto in configData["proto"]:
        index = oneProto["index"]
        protoContent = file(SERVER_DIR+"proto/"+oneProto["filename"],'r').read()

        #更新到配置数据库中
        sql = "UPDATE `{}` SET `proto`='{}' WHERE `index`='{}'".format(
            PROTOTABLE,
            pymysql.escape_string(protoContent),
            index)

        print("update proto sql = %s"%(sql))

        cursor.execute(sql)
        conn.commit()

    #4.更新lua
    for oneLua in configData["lua"]:
        index = oneLua["index"]
        luaContent = file(SERVER_DIR+"lua/"+oneLua["filename"],'r').read()

        if oneLua["filename"] == "award_1_42004_comModel.lua":
            #commmodel中需要替换redis判断
            luaContent = luaContent.replace('comm_model.islocalredis = false', 'comm_model.islocalredis = true')

        #更新到配置数据库中
        sql = "UPDATE `{}` SET `lua`='{}' WHERE `index`='{}'".format(
            LUATABLE,
            pymysql.escape_string(luaContent),
            index)

        print("update lua sql = %s"%(sql))

        cursor.execute(sql)
        conn.commit()

    #5.关闭数据库连接
    cursor.close()
    conn.close()

    #6.重启dbp server
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=DBPHOST, port=22, username=DBPUSER, password=DBPPASSWD)
    stdin, stdout, stderr = ssh.exec_command('cd /data/BackGround/11802/DBProcedureSvr/;rm -rf log/*;./r.sh')

    # 获取命令结果
    result = stdout.read()
    print(result)

    # 关闭连接
    ssh.close()

    #7.根据房间列表更新so、Config.zip,并重启房间
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=GSHOST, port=22, username=GSUSER, password=GSPASSWD)

    for levelid in configData["so"]:
        #更新so和zip
        with closing(scpclient.Write(ssh.get_transport(), '/data/11802/svrprocess/GameProcess/')) as scp:
            scp.send_file(SERVER_DIR+'so/liblogic.so', True, remote_filename = 'xdby33_'+str(levelid)+'.so')

        with closing(scpclient.Write(ssh.get_transport(), '/data/11802/GameSvr/42004_'+str(levelid)+'/')) as scp:
            scp.send_file(SERVER_DIR+'so/Config.zip', True, remote_filename = 'Config.zip')

        #重启房间
        stdin, stdout, stderr = ssh.exec_command('cd /data/11802/GameSvr/42004_'+str(levelid)+'/;./run_'+str(levelid)+'.sh')
        print(stdout.read())

        print("Success to deploy test server, levelid %d"%levelid)

    #关闭连接
    ssh.close()

    print "Success to deploy all test server!\n"

if __name__ == '__main__':
    DeployServer()
