#!/bin/env python
#-*- coding: utf-8 -*-
from GameProtocol import CS_pb2, MsgID_pb2, Common_pb2
from PressRobot import ENUM_ROBOT_TYPE_GAME_SERVER
import PressRobot
import math
import time


class GamePressRobot(PressRobot.PressRobot):
    def __init__(self, host, port, RobotUin):
        PressRobot.PressRobot.__init__(self, host, port, ENUM_ROBOT_TYPE_GAME_SERVER, RobotUin)
        
    def __del__(self):
        PressRobot.PressRobot.__del__(self)
        
    def RobotFunctionRun(self):
        
        #首先发送Login请求
        stLoginMsg = CS_pb2.ProtocolCSMsg()
        self.GenerateMsgHead(stLoginMsg, MsgID_pb2.MSGID_ZONE_LOGINSERVER_REQUEST)
        stLoginMsg.m_stMsgHead.m_strSessionKey = "qlYal0H1FRCWIBWnKiezn2k5K5Cuz58Di9kAYL+Pup0="

        stZoneLoginReq = stLoginMsg.m_stMsgBody.m_stZone_LoginServer_Request
        stZoneLoginReq.stRoleID.uin = self.GetRobotUin()
        stZoneLoginReq.stRoleID.uiSeq = 53100011

        self.RobotSendMsg(stLoginMsg)
        
        print "Send Login Msg"
        
        #接收Login
        stResponseMsg = self.RobotRecvMsgByID(MsgID_pb2.MSGID_ZONE_LOGINSERVER_RESPONSE)
        stLoginResp = stResponseMsg.m_stMsgBody.m_stZone_LoginServer_Response
        if(stLoginResp.iResult != 0):
            raise RuntimeError("Failed to login to game server, result %d, uin %u\n"%(stLoginResp.iResult, self.GetRobotUin()));
        
        #让角色循环移动
        while(1):
            #第一段移动
            startPos = Common_pb2.UnitPosition();
            endPos = Common_pb2.UnitPosition();
            startPos.uPosX = 974
            startPos.uPosY = 839
            endPos.uPosX = 760
            endPos.uPosY = 560
            self.RobotMovePosition(startPos, endPos);
            
            #第二段移动
            startPos.uPosX = 760
            startPos.uPosY = 560
            endPos.uPosX = 420
            endPos.uPosY = 690
            self.RobotMovePosition(startPos, endPos);
        
            #第三段移动
            startPos.uPosX = 420
            startPos.uPosY = 690
            endPos.uPosX = 974
            endPos.uPosY = 839
            self.RobotMovePosition(startPos, endPos);
            
            #sleep 3s
            time.sleep(3);
            
        #print "Success to test pve fight, uin %u\n" %(self.GetRobotUin())
        
        return
    
    def RobotMovePosition(self, startPos, endPos):
        #发送移动消息
        stMoveMsg = CS_pb2.ProtocolCSMsg()
        self.GenerateMsgHead(stMoveMsg, MsgID_pb2.MSGID_ZONE_MOVEPOSITION_REQUEST)
       
        stMoveReq = stMoveMsg.m_stMsgBody.m_stMovePosition_Request
        MyStartPos = stMoveReq.stPath.stPoses.add()
        MyEndPos = stMoveReq.stPath.stPoses.add()
        MyStartPos.uPosX = startPos.uPosX
        MyStartPos.uPosY = startPos.uPosY
        MyEndPos.uPosX = endPos.uPosX
        MyEndPos.uPosY = endPos.uPosY
        self.RobotSendMsg(stMoveMsg);

        #接收返回
        stResponseMsg = self.RobotRecvMsgByID(MsgID_pb2.MSGID_ZONE_MOVEPOSITION_RESPONSE)
        stMoveResp = stResponseMsg.m_stMsgBody.m_stMovePosition_Response
        if(stMoveResp.iResult != 0):
            raise RuntimeError("Failed to do role move, result %d, uin %u\n"%(stMoveResp.iResult, self.GetRobotUin()));
        
        #确保移动完成
        iDistance = math.sqrt(math.pow((startPos.uPosX-endPos.uPosX),2)+math.pow((startPos.uPosY-endPos.uPosY),2));
        time.sleep(iDistance/400.0)
        
        #sleep()