#!/bin/env python
#-*- coding: utf-8 -*-
from AsyncPressRobot import ENUM_ROBOT_TYPE_GAMESERVER
import AsyncPressRobot
from GameProtocol import CS_pb2, MsgID_pb2
from google.protobuf.text_format import MessageToString
from tornado.ioloop import IOLoop


#游戏服务器的消息Handler
g_GameSvrRecvMsgHandler = {}

def LoginRespHandler(AsyncGamePressRobot, RecvProtoMsg):
    #登录请求的响应包
    stLoginResp = RecvProtoMsg.m_stMsgBody.m_stZone_LoginServer_Response
    if(stLoginResp.iResult != 0):
        raise RuntimeError("Failed to login game server, ret 0x%0x\n", stLoginResp.iResult)
    
    #print "Success login to game server, uin %u\n"%(AsyncGamePressRobot.GetRobotUin())
    
    #发送开始PVE关卡战斗的包
    stStartPveMsg = CS_pb2.ProtocolCSMsg()
    AsyncGamePressRobot.GenerateMsgHead(stStartPveMsg, MsgID_pb2.MSGID_ZONE_PVESTARTFIGHT_REQUEST)
    
    #封装开始PVE关卡战斗的消息体
    stStartPveReq = stStartPveMsg.m_stMsgBody.m_stZone_PveStartFight_Request
    stStartPveReq.uPinstanceID = 3010
    stStartPveReq.uCrossID = 30101
    
    AsyncGamePressRobot.RobotSendMsg(stStartPveMsg)
    
    #print "Success to send start pve Msg"
    
    #print "Try to create account %u\n" %(AsyncAccountPressRobot.GetRobotUin())
    
def StartPveRespHandler(AsyncGamePressRobot, RecvProtoMsg):
    #开始PVE战斗返回的包
    stStartPveResp = RecvProtoMsg.m_stMsgBody.m_stZone_PveStartFight_Response
    if(stStartPveResp.iResult != 0):
        return 
        #raise RuntimeError("Failed to start pve fight, uin %u\n" %(AsyncGamePressRobot.GetRobotUin()))
    
    print "Success to start pve, uin %u\n" %(AsyncGamePressRobot.GetRobotUin())
    
    #发送PVE战斗结束的返回包
    stFinPveMsg = CS_pb2.ProtocolCSMsg()
    AsyncGamePressRobot.GenerateMsgHead(stFinPveMsg, MsgID_pb2.MSGID_ZONE_PVEFINFIGHT_REQUEST)

    #封装PVE战斗结束的消息体
    stFinPveReq = stFinPveMsg.m_stMsgBody.m_stZone_PveFinFight_Request
    stFinPveReq.uPinstanceID = 3010
    stFinPveReq.uCrossID = 30101
    stFinPveReq.bIsWin = True

    AsyncGamePressRobot.RobotSendMsg(stFinPveMsg)
    
def FinPveRespHandler(AsyncGamePressRobot, RecvProtoMsg):
    #结束PVE战斗的返回包
    stFinPveResp = RecvProtoMsg.m_stMsgBody.m_stZone_PveFinFight_Response
    if(stFinPveResp.iResult != 0):
        return 
        raise RuntimeError("Failed to fin pve fight, uin %u\n" %(AsyncGamePressRobot.GetRobotUin()))
    
    print "Success to fin pve, uin %u\n" %(AsyncGamePressRobot.GetRobotUin())
    
    #发送开始PVE战斗的请求，重新开始PVE
    stStartPveMsg = CS_pb2.ProtocolCSMsg()
    AsyncGamePressRobot.GenerateMsgHead(stStartPveMsg, MsgID_pb2.MSGID_ZONE_PVESTARTFIGHT_REQUEST)

    #封装PVE战斗的请求消息体
    stStartPveReq = stStartPveMsg.m_stMsgBody.m_stZone_PveStartFight_Request
    stStartPveReq.uPinstanceID = 3010
    stStartPveReq.uCrossID = 30101
    
    AsyncGamePressRobot.RobotSendMsg(stStartPveMsg)

class AsyncGamePressRobot(AsyncPressRobot.AsyncPressRobot):
    def __init__(self, host, port, RobotUin):
        AsyncPressRobot.AsyncPressRobot.__init__(self, host, port, ENUM_ROBOT_TYPE_GAMESERVER, RobotUin)
        
        self.RegisterGameRecvMsgHandlers()
        
    def __del__(self):
        AsyncPressRobot.AsyncPressRobot.__del__(self)
    
    def RegisterGameRecvMsgHandlers(self):
        g_GameSvrRecvMsgHandler[MsgID_pb2.MSGID_ZONE_LOGINSERVER_RESPONSE] = LoginRespHandler
        g_GameSvrRecvMsgHandler[MsgID_pb2.MSGID_ZONE_PVESTARTFIGHT_RESPONSE] = StartPveRespHandler
        g_GameSvrRecvMsgHandler[MsgID_pb2.MSGID_ZONE_PVEFINFIGHT_RESPONSE] = FinPveRespHandler
        
        return     
    
    def SendInitProtoData(self):
        #通过发送登录请求包驱动机器人
        stLoginMsg = CS_pb2.ProtocolCSMsg()
        self.GenerateMsgHead(stLoginMsg, MsgID_pb2.MSGID_ZONE_LOGINSERVER_REQUEST)
        
        stLoginReq = stLoginMsg.m_stMsgBody.m_stZone_LoginServer_Request
        stLoginReq.uin = self.GetRobotUin()
        stLoginReq.iWorldID = 1
        
        self.RobotSendMsg(stLoginMsg)
        
    def RobotFunctionRun(self, RecvProtoMsg):
        
        #print "Game Press Robot receive msg %d\n"%(RecvProtoMsg.m_stMsgHead.m_uiMsgID)
        
        if(g_GameSvrRecvMsgHandler.has_key(RecvProtoMsg.m_stMsgHead.m_uiMsgID)):
            g_GameSvrRecvMsgHandler[RecvProtoMsg.m_stMsgHead.m_uiMsgID](self, RecvProtoMsg)
            
        return 