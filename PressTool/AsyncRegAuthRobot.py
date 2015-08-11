#!/bin/env python
#-*- coding: utf-8 -*-
from AsyncPressRobot import ENUM_ROBOT_TYPE_REGAUTHSERVER
import AsyncPressRobot
from GameProtocol import CS_pb2, MsgID_pb2
from google.protobuf.text_format import MessageToString

from tornado.ioloop import IOLoop

#RegAuth的消息处理函数
g_RegAuthRecvMsgHandler = {}

def RegisterRespHandler(AsyncRegAuthPressRobot, RecvProtoMsg):
    #注册帐号的返回
    stRegResp = RecvProtoMsg.m_stMsgBody.m_stRegAuth_RegAccount_Response
    if(stRegResp.iResult != 0):
        raise RuntimeError("Failed to register account, ret 0x%0x\n", stRegResp.iResult)
    
    #print "Success to register account %d\n" %(AsyncRegAuthPressRobot.GetRobotUin())
    
    #注册帐号成功，发送认证请求
    stAuthAccountMsg = CS_pb2.ProtocolCSMsg()
    AsyncRegAuthPressRobot.GenerateMsgHead(stAuthAccountMsg, MsgID_pb2.MSGID_REGAUTH_AUTHACCOUNT_REQUEST)
    
    #发送认证帐号的请求
    stAuthAccountReq = stAuthAccountMsg.m_stMsgBody.m_stRegAuth_AuthAccount_Request
    stAuthAccountReq.stAccountID.iAccountType = 1
    stAuthAccountReq.stAccountID.strAccount = "jason"+str(AsyncRegAuthPressRobot.GetRobotUin())
    
    AsyncRegAuthPressRobot.RobotSendMsg(stAuthAccountMsg)
    
    #print "Try to create account %u\n" %(AsyncAccountPressRobot.GetRobotUin())
    
def AuthRespHandler(AsyncRegAuthPressRobot, RecvProtoMsg):
    #认证帐号返回消息的处理
    stAuthResp = RecvProtoMsg.m_stMsgBody.m_stRegAuth_AuthAccount_Response
    if(stAuthResp.iResult != 0):
        #print "Failed to create account %u\n" %(AsyncRegAuthPressRobot.GetRobotUin())
        
        #发送注册帐号的请求
        stRegAccountMsg = CS_pb2.ProtocolCSMsg()
        AsyncRegAuthPressRobot.GenerateMsgHead(stRegAccountMsg, MsgID_pb2.MSGID_REGAUTH_REGACCOUNT_REQUEST)
        
        #封装注册帐号的消息体
        stRegAccountReq = stRegAccountMsg.m_stMsgBody.m_stRegAuth_RegAccount_Request
        stRegAccountReq.iRegOpType = 1
        stRegAccountReq.stAccountID.iAccountType = 1
        stRegAccountReq.stAccountID.strAccount = "jason"+str(AsyncRegAuthPressRobot.GetRobotUin())
        
        AsyncRegAuthPressRobot.RobotSendMsg(stRegAccountMsg)
        
        return 
    
    #print "Success to auth account %u\n" %(AsyncRegAuthPressRobot.GetRobotUin())

    #将socket fd从监听事件列表中去掉
    IOLoop.instance().remove_handler(AsyncRegAuthPressRobot.GetRobotFD())

    AsyncRegAuthPressRobot.GetRobotSock().close()

class AsyncRegAuthPressRobot(AsyncPressRobot.AsyncPressRobot):
    def __init__(self, host, port, RobotUin):
        AsyncPressRobot.AsyncPressRobot.__init__(self, host, port, ENUM_ROBOT_TYPE_REGAUTHSERVER, RobotUin)
        
        self.RegisterRegAuthMsgHandlers()
        
    def __del__(self):
        AsyncPressRobot.AsyncPressRobot.__del__(self)
    
    def RegisterRegAuthMsgHandlers(self):
        g_RegAuthRecvMsgHandler[MsgID_pb2.MSGID_REGAUTH_REGACCOUNT_RESPONSE] = RegisterRespHandler
        g_RegAuthRecvMsgHandler[MsgID_pb2.MSGID_REGAUTH_AUTHACCOUNT_RESPONSE] = AuthRespHandler
        
        return     
    
    def SendInitProtoData(self):
        #由认证帐号的请求开始驱动压测机器人
        stAuthAccountMsg = CS_pb2.ProtocolCSMsg()
        self.GenerateMsgHead(stAuthAccountMsg, MsgID_pb2.MSGID_REGAUTH_AUTHACCOUNT_REQUEST)
        
        stAuthReq = stAuthAccountMsg.m_stMsgBody.m_stRegAuth_AuthAccount_Request
        stAuthReq.stAccountID.strAccount = "jason"+str(self.GetRobotUin())
        stAuthReq.stAccountID.iAccountType = 1
        
        self.RobotSendMsg(stAuthAccountMsg)
        
    def RobotFunctionRun(self, RecvProtoMsg):
        #处理收到的消息返回
        #print MessageToString(RecvProtoMsg)
        
        #print "RobotFunction uin:%u, FD:%d\n" %(self.GetRobotUin(), self.GetRobotFD())
        #print "Recv Msg ID %d" %(RecvProtoMsg.m_stMsgHead.m_uiMsgID)
        
        fMsgHandler = g_RegAuthRecvMsgHandler[RecvProtoMsg.m_stMsgHead.m_uiMsgID]
        if(fMsgHandler != None):
            fMsgHandler(self, RecvProtoMsg)
            
        return 