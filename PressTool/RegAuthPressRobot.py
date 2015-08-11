#!/bin/env python
#-*- coding: utf-8 -*-
from GameProtocol import CS_pb2, MsgID_pb2
from PressRobot import ENUM_ROBOT_TYPE_REGAUTH_SERVER
import PressRobot


class RegAuthPressRobot(PressRobot.PressRobot):
    def __init__(self, host, port, RobotUin):
        PressRobot.PressRobot.__init__(self, host, port, ENUM_ROBOT_TYPE_REGAUTH_SERVER, RobotUin)
        
    def __del__(self):
        PressRobot.PressRobot.__del__(self)
        
    def RobotFunctionRun(self):
        
        #首先测试创建游客帐号
        stRegisterMsg = CS_pb2.ProtocolCSMsg()
        self.GenerateMsgHead(stRegisterMsg, MsgID_pb2.MSGID_REGAUTH_REGACCOUNT_REQUEST)

        stRegisterReq = stRegisterMsg.m_stMsgBody.m_stRegAuth_RegAccount_Request
        stRegisterReq.stAccountID.strAccount = "Jason"+str(self.GetRobotUin())
        stRegisterReq.stAccountID.iAccountType = 1
        stRegisterReq.strPassword = "Jason"
        
        self.RobotSendMsg(stRegisterMsg)
        
        #接收增加游客帐号的返回
        stResponseMsg = self.RobotRecvMsgByID(MsgID_pb2.MSGID_REGAUTH_REGACCOUNT_RESPONSE)
        stRegisterResp = stResponseMsg.m_stMsgBody.m_stRegAuth_RegAccount_Response
        if(stRegisterResp.iResult == 150999042):
            print "Account %d is registered!\n" %(self.GetRobotUin())
        elif(stRegisterResp.iResult != 0):
            raise RuntimeError("Failed to register account, result %d\n"%(stRegisterResp.iResult));
        else:
            print "Success to register account %d\n"%(self.GetRobotUin())
        
        #发送登录请求，登录帐号平台
        stAuthMsg = CS_pb2.ProtocolCSMsg()
        self.GenerateMsgHead(stAuthMsg, MsgID_pb2.MSGID_REGAUTH_AUTHACCOUNT_REQUEST)

        stAuthReq = stAuthMsg.m_stMsgBody.m_stRegAuth_AuthAccount_Request
        stAuthReq.stAccountID.strAccount = "Jason"+str(self.GetRobotUin())
        stAuthReq.stAccountID.iAccountType = 1
        stAuthReq.strPassword = "Jason";
        
        self.RobotSendMsg(stAuthMsg)
        
        #接收登录请求的返回
        stResponseMsg = self.RobotRecvMsgByID(MsgID_pb2.MSGID_REGAUTH_AUTHACCOUNT_RESPONSE)
        if(stResponseMsg.m_stMsgBody.m_stRegAuth_AuthAccount_Response.iResult != 0):
            raise RuntimeError("Failed to do auth %u, ret %d\n", self.GetRobotUin(), stResponseMsg.m_stMsgBody.m_stRegAuth_AuthAccount_Response.iResult);
        
        print "Success to do auth account %d, session key %s\n" %(stResponseMsg.m_stMsgBody.m_stRegAuth_AuthAccount_Response.uin, stResponseMsg.m_stMsgBody.m_stRegAuth_AuthAccount_Response.strSessionKey)
        
        return 