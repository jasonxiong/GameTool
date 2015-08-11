#!/bin/env python
#-*- coding: utf-8 -*-
#from abc import abstractmethod
import socket
import struct
import threading

from GameProtocol import CS_pb2


#非法的机器人类型
ENUM_ROBOT_TYPE_INVALID = 0

#帐号服务器的机器人
ENUM_ROBOT_TYPE_ACCOUNT_SERVER = 1

#游戏服务器的机器人
ENUM_ROBOT_TYPE_GAME_SERVER = 2

#测试注册认证服务器的机器人
ENUM_ROBOT_TYPE_REGAUTH_SERVER = 3

class PressRobot(object):
    __robot_sock = None
    __robot_thread = None
    __thread_type = ENUM_ROBOT_TYPE_INVALID
    __robot_uin = 0
    
    def __init__(self, strHost, iPort, iType, RobotUin):
        self.__robot_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #print "host %s, port %d, type %d" %(strHost, iPort, iType)
        self.__robot_sock.connect((strHost, iPort))
        
        self.__thread_type = iType
        
        self.__robot_thread = threading.Thread(target=self.RobotFunctionRun)
    
        self.__robot_uin = RobotUin
    
    def __del__(self):
        self.__thread_type = ENUM_ROBOT_TYPE_INVALID
        self.__robot_sock.close()
    
    def GetThread(self):
        return self.__robot_thread
    
    def GetRobotSock(self):
        return self.__robot_sock
    
    def GetThreadType(self):
        return self.__thread_type
    
    def GetRobotUin(self):
        return self.__robot_uin
    
    #@abstractmethod
    def RobotFunctionRun(self):
        raise RuntimeError("This function should be realized by child class!\n");
    
    def RobotRun(self):
        self.__robot_thread.start()
        pass
    
    def RobotWait(self):
        self.__robot_thread.join()
    
    def GenerateMsgHead(self, stGameMsg, iMsgID):
        stGameMsg.m_stMsgHead.m_uiMsgID = iMsgID
        stGameMsg.m_stMsgHead.m_uin = self.__robot_uin
        
    def RobotRecvMsgByID(self, iMsgID):
        while(1):
            #self.__robot_sock.settimeout(20)
            
            #先收2字节的包长度
            strRecvMsgLen = "";
            while(len(strRecvMsgLen) < 2):
                strRecvMsgLen += self.__robot_sock.recv(2)
                
            arRecvMsgLen = struct.unpack("H", strRecvMsgLen)
            iRecvMsgLen = socket.ntohs(arRecvMsgLen[0])
            
            iLeftLen = iRecvMsgLen-2
            RecvMsg = ""
            while iLeftLen>0:  
                RecvMsg = RecvMsg + self.__robot_sock.recv(iLeftLen)
                iLeftLen = iLeftLen - len(RecvMsg)
            
            #RecvMsg = self.ClientConn.recv(40960)
            if len(RecvMsg) == 0:
                raise RuntimeError("Socket recv data error!");
        
            MsgBodyData = RecvMsg

            RetProtoMsg = CS_pb2.ProtocolCSMsg()
            RetProtoMsg.ParseFromString(MsgBodyData)
            
            #print "Recv Proto MSGID %d\n" %(RetProtoMsg.m_stMsgHead.m_uiMsgID)
            
            if(RetProtoMsg.m_stMsgHead.m_uiMsgID == iMsgID):
                return RetProtoMsg
        
        raise RuntimeError("Failed to recv msg by id %d" %iMsgID)
    
    def RobotSendMsg(self, stGameMsg):
        SerializedMsg = stGameMsg.SerializeToString()
        
        SendBuff = struct.pack("H", socket.htons(stGameMsg.ByteSize()+2)) + SerializedMsg
        
        MsgLen = len(SendBuff)       
        TotalSent = 0
        
        while TotalSent < MsgLen:
            SendLen = self.__robot_sock.send(SendBuff[TotalSent:])
            if SendLen == 0:
                raise RuntimeError("Socket connection is broken!")
            TotalSent += SendLen;
    
    