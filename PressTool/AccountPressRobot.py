#!/bin/env python
#-*- coding: utf-8 -*-
from GameProtocol import CS_pb2, MsgID_pb2
from PressRobot import ENUM_ROBOT_TYPE_ACCOUNT_SERVER
import PressRobot


class AccountPressRobot(PressRobot.PressRobot):
    def __init__(self, host, port, RobotUin):
        PressRobot.PressRobot.__init__(self, host, port, ENUM_ROBOT_TYPE_ACCOUNT_SERVER, RobotUin)
        
    def __del__(self):
        PressRobot.PressRobot.__del__(self)
        
    def RobotFunctionRun(self):
        
        #棣栧厛鍙戦�丩istRole璇锋眰
        stListRoleMsg = CS_pb2.ProtocolCSMsg()
        self.GenerateMsgHead(stListRoleMsg, MsgID_pb2.MSGID_ACCOUNT_LISTROLE_REQUEST)

        stAccountListReq = stListRoleMsg.m_stMsgBody.m_stAccountListRoleRequest
        stAccountListReq.uin = self.GetRobotUin()
        stAccountListReq.world = 1
        
        self.RobotSendMsg(stListRoleMsg)
        
        #鎺ユ敹ListRole杩斿洖
        stResponseMsg = self.RobotRecvMsgByID(MsgID_pb2.MSGID_ACCOUNT_LISTROLE_RESPONSE)
        stAccountListResp = stResponseMsg.m_stMsgBody.m_stAccountListRoleResponse
        if(stAccountListResp.iResult != 0):
            raise RuntimeError("Failed to list role, result %d\n"%(stAccountListResp.iResult));
        elif(len(stAccountListResp.roles) != 0):
            print("role already exist, uin %u, seq %u\n"%(stAccountListResp.roles[0].stRoleID.uin,stAccountListResp.roles[0].stRoleID.uiSeq));
            return;
        
        #濡傛灉瑙掕壊瀛樺湪鍒欑洿鎺ヨ繑鍥�
        #if(stAccountListResp.bRoleExist):
        #    print "account uin %u exists, thread name %s!\n" %(self.GetRobotUin(), self.GetThread().getName())
        #    return 
        
        #瑙掕壊涓嶅瓨鍦紝鍙戦�丆reateRole鐨勮姹�
        stCreateRoleMsg = CS_pb2.ProtocolCSMsg()
        self.GenerateMsgHead(stCreateRoleMsg, MsgID_pb2.MSGID_ACCOUNT_CREATEROLE_REQUEST)
        stCreateRoleMsg.m_stMsgHead.m_strSessionKey = "qlYal0H1FRCWIBWnKiezn2k5K5Cuz58Di9kAYL+Pup0="

        stAccountCreateReq = stCreateRoleMsg.m_stMsgBody.m_stAccountCreateRoleRequest
        #stAccountCreateReq.szNickName = "Jason"+str(self.GetRobotUin())
        stAccountCreateReq.uin = self.GetRobotUin()
        stAccountCreateReq.worldID = 1
        stAccountCreateReq.szNickName = "aaaa1%u"%(self.GetRobotUin());
        #stAccountCreateReq.uGender = 101
        
        self.RobotSendMsg(stCreateRoleMsg)
        
        #鎺ユ敹CreateRole鐨勮繑鍥�,鍑洪敊鍒欐墦鍗伴敊璇爜
        stResponseMsg = self.RobotRecvMsgByID(MsgID_pb2.MSGID_ACCOUNT_CREATEROLE_RESPONSE)
        if(stResponseMsg.m_stMsgBody.m_stAccountCreateRoleResponse.iResult != 0):
            raise RuntimeError("Failed to create %d, ret %d\n", self.GetRobotUin(), stResponseMsg.m_stMsgBody.m_stAccountCreateRoleResponse.iResult);
        
        print "Success to create account %d, thread name %s\n" %(self.GetRobotUin(), self.GetThread().getName())
        
        return 