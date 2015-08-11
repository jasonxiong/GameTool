#!/bin/env python
#-*- coding: utf-8 -*- 

import sys

from AccountPressRobot import AccountPressRobot
from GamePressRobot import GamePressRobot
from PressRobot import ENUM_ROBOT_TYPE_ACCOUNT_SERVER, \
    ENUM_ROBOT_TYPE_GAME_SERVER, ENUM_ROBOT_TYPE_REGAUTH_SERVER
from RegAuthPressRobot import RegAuthPressRobot


def CreateRobotByType(strHost, iPort, iType, RobotUin):
    if(iType == ENUM_ROBOT_TYPE_ACCOUNT_SERVER):
        return AccountPressRobot(strHost, iPort, RobotUin)
    elif(iType == ENUM_ROBOT_TYPE_GAME_SERVER):
        return GamePressRobot(strHost, iPort, RobotUin)
    elif(iType == ENUM_ROBOT_TYPE_REGAUTH_SERVER):
        return RegAuthPressRobot(strHost, iPort, RobotUin)

def Usage():
    print "Usage: ./PressTestMain.py <Host> <Port> <Type> <BeginUin> <RobotNum>"
    print "        Type: 1(AccountServer)  2(GameServer) 3(RegAuthServer)"
    

def PressTestMain(argv):
    if(len(argv) != 5):
        Usage()
        exit(-1)
    
    strHost = argv[0]
    iPort = int(argv[1])
    iType = int(argv[2])
    
    iBeginUin = int(argv[3])
    iRobotNum = int(argv[4])
    
    print "Total press test for %d robots, type %d" %(iRobotNum, iType)
    
    TotalRobots = []
    
    for uin in range(iBeginUin, iBeginUin+iRobotNum):
        TotalRobots.append(CreateRobotByType(strHost, iPort, iType, uin))
    

    for Robot in TotalRobots:
        Robot.RobotRun()
        
    for Robot in TotalRobots:
        Robot.RobotWait()

if __name__ == "__main__":
    try:
        PressTestMain(sys.argv[1:])
    except KeyboardInterrupt:
        pass
    