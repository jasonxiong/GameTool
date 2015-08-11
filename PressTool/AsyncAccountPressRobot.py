#!/bin/env python
#-*- coding: utf-8 -*-
from AsyncPressRobot import ENUM_ROBOT_TYPE_ACCOUNTSERVER
import AsyncPressRobot
from GameProtocol import CS_pb2, MsgID_pb2
from GameProtocol.MsgID_pb2 import MSGID_ACCOUNT_LISTROLE_RESPONSE, \
    MSGID_ACCOUNT_CREATEROLE_RESPONSE, MSGID_ACCOUNT_LISTROLE_REQUEST
from PressRobot import ENUM_ROBOT_TYPE_ACCOUNT_SERVER
import PressRobot
from google.protobuf.text_format import MessageToString


#Account 压测机器人的消息处理函数集
g_AccountRecvMsgHandler = {}

def AccountListRoleRespHandler(AsyncAccountPressRobot, RecvProtoMsg):
    #获取ListRole的消息体
    stListRoleResp = RecvProtoMsg.m_stMsgBody.m_stAccountListRoleResponse
    if(stListRoleResp.iResult != 0):
        raise RuntimeError("Failed to list game role, ret 0x%0x\n", stListRoleResp.iResult)
    
    if(stListRoleResp.bRoleExist):
        AsyncAccountPressRobot.GetRobotSock().close()
        print "Account uin %u already exists!\n" %(AsyncAccountPressRobot.GetRobotUin())
        return
    
    #没有帐号角色，发送创建帐号的请求
    stCreateRoleMsg = CS_pb2.ProtocolCSMsg()
    AsyncAccountPressRobot.GenerateMsgHead(stCreateRoleMsg, MsgID_pb2.MSGID_ACCOUNT_CREATEROLE_REQUEST)
    stCreateRoleMsg.m_stMsgHead.m_strSessionKey = "qlYal0H1FRCWIBWnKiezn2k5K5Cuz58Di9kAYL+Pup0="
    
    #封装消息体
    stCreateRoleReq = stCreateRoleMsg.m_stMsgBody.m_stAccountCreateRoleRequest
    stCreateRoleReq.worldID = 1
    stCreateRoleReq.szNickName = "jasonxiong"+str(AsyncAccountPressRobot.GetRobotUin())
    stCreateRoleReq.uin = AsyncAccountPressRobot.GetRobotUin()
    
    AsyncAccountPressRobot.RobotSendMsg(stCreateRoleMsg)
    
    #print "Try to create account %u\n" %(AsyncAccountPressRobot.GetRobotUin())
    
def AccountCreateRoleRespHandler(AsyncAccountPressRobot, RecvProtoMsg):
    #获取CreateRole的消息体
    stCreateRoleResp = RecvProtoMsg.m_stMsgBody.m_stAccountCreateRoleResponse
    if(stCreateRoleResp.iResult != 0):
        print "Failed to create account %u\n" %(AsyncAccountPressRobot.GetRobotUin())
        return 
    
    print "Success to create account %u\n" %(AsyncAccountPressRobot.GetRobotUin())

    AsyncAccountPressRobot.GetRobotSock().close()

class AsyncAccountPressRobot(AsyncPressRobot.AsyncPressRobot):
    def __init__(self, host, port, RobotUin):
        AsyncPressRobot.AsyncPressRobot.__init__(self, host, port, ENUM_ROBOT_TYPE_ACCOUNTSERVER, RobotUin)
        
        self.RegisterAccountMsgHandlers()
        
    def __del__(self):
        AsyncPressRobot.AsyncPressRobot.__del__(self)
    
    def RegisterAccountMsgHandlers(self):
        
        g_AccountRecvMsgHandler[MSGID_ACCOUNT_LISTROLE_RESPONSE] = AccountListRoleRespHandler
        g_AccountRecvMsgHandler[MSGID_ACCOUNT_CREATEROLE_RESPONSE] = AccountCreateRoleRespHandler
        
        return     
    
    def SendInitProtoData(self):
        #发送机器人起始驱动数据包, ListRole
        stListRoleMsg = CS_pb2.ProtocolCSMsg()
        self.GenerateMsgHead(stListRoleMsg, MSGID_ACCOUNT_LISTROLE_REQUEST)
        
        stListRoleReq = stListRoleMsg.m_stMsgBody.m_stAccountListRoleRequest
        stListRoleReq.uin = self.GetRobotUin()
        stListRoleReq.world = 1
        
        self.RobotSendMsg(stListRoleMsg)
        
    def RobotFunctionRun(self, RecvProtoMsg):
        #先打印收到的消息
        #print MessageToString(RecvProtoMsg)
        
        #print "RobotFunction uin:%u, FD:%d\n" %(self.GetRobotUin(), self.GetRobotFD())
        
        fMsgHandler = g_AccountRecvMsgHandler[RecvProtoMsg.m_stMsgHead.m_uiMsgID]
        if(fMsgHandler != None):
            fMsgHandler(self, RecvProtoMsg)
            
        return 