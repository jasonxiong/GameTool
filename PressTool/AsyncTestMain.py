#!/bin/env python
#-*- coding: utf-8 -*- 

import sys
import threading
import time

from AsyncAccountPressRobot import AsyncAccountPressRobot
from AsyncGamePressRobot import AsyncGamePressRobot
from AsyncPressRobot import ENUM_ROBOT_TYPE_ACCOUNTSERVER, \
    ENUM_ROBOT_TYPE_GAMESERVER, ENUM_ROBOT_TYPE_REGAUTHSERVER, g_FDRobotMap
from AsyncRegAuthRobot import AsyncRegAuthPressRobot
import tornado.ioloop


def CreatePressRobot(strHost, iPort, iRobotType, uin):
    if(iRobotType == ENUM_ROBOT_TYPE_ACCOUNTSERVER):
        stPressRobot = AsyncAccountPressRobot(strHost, iPort, uin)
        g_FDRobotMap[stPressRobot.GetRobotFD()] = stPressRobot
    elif(iRobotType == ENUM_ROBOT_TYPE_REGAUTHSERVER):
        stPressRobot = AsyncRegAuthPressRobot(strHost, iPort, uin)
        g_FDRobotMap[stPressRobot.GetRobotFD()] = stPressRobot
    elif(iRobotType == ENUM_ROBOT_TYPE_GAMESERVER):
        stPressRobot = AsyncGamePressRobot(strHost, iPort, uin)
        g_FDRobotMap[stPressRobot.GetRobotFD()] = stPressRobot
    else:
        raise RuntimeError("Failed to create press robot, invalid type %d" %(iRobotType));

def Usage():
    print "./AsyncPressTestMain.py <strHost> <Port> <RobotType> <BeginUin> <Num>"

def AsyncPressTestMain(argv):
    if(len(argv) != 5):
        Usage()
        return 
    
    strHost = argv[0]
    iPort = int(argv[1])
    iRobotType = int(argv[2])
    uBeginUin = int(argv[3])
    uNum = int(argv[4])

    for uin in range(uBeginUin, uBeginUin+uNum):
        CreatePressRobot(strHost, iPort, iRobotType, uin)
    
    tornado.ioloop.IOLoop.instance().start()
    
    pass

if __name__ == "__main__":
    try:
        AsyncPressTestMain(sys.argv[1:])
    except KeyboardInterrupt:
        pass 
