#!/bin/env python
#-*- coding: utf-8 -*-
#from abc import abstractmethod
from fileinput import fileno
import socket
import struct
import threading

from GameProtocol import CS_pb2
from tornado.ioloop import IOLoop


ENUM_ROBOT_TYPE_ACCOUNTSERVER = 1
ENUM_ROBOT_TYPE_GAMESERVER = 2
ENUM_ROBOT_TYPE_REGAUTHSERVER = 3

g_FDRobotMap = {}

class AsyncPressRobot(object):
    __robot_sock = None
    __robot_uin = 0
    __recv_buff = ""
    __robot_fd = -1
    
    def __init__(self, strHost, iPort, iType, RobotUin):
        self.__robot_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__robot_sock.connect((strHost, iPort))
    
        #设置连接为非阻塞
        self.__robot_sock.setblocking(False)
    
        self.__robot_uin = RobotUin
        
        self.__robot_fd = self.__robot_sock.fileno()
    
        #g_FDRobotMap[self.__robot_fd] = self
    
        #将socket fd增加到事件监听列表中去
        IOLoop.instance().add_handler(self.__robot_fd, self.ClientDataHandler, IOLoop.READ)
    
        #发送压测机器人起始驱动数据包
        self.SendInitProtoData()
    
    def __del__(self):
        self.__robot_sock.close()
    
    def GetRobotSock(self):
        return self.__robot_sock
    
    def GetRobotUin(self):
        return self.__robot_uin
    
    def GetRecvBuff(self):
        return self.__recv_buff
    
    def GetRobotFD(self):
        return self.__robot_fd
    
    def ClientDataHandler(self, fd, event):
        if(event&IOLoop.READ):
            stPressRobot = g_FDRobotMap[self.__robot_fd]
            #print "FD: %d, uin %u\n" %(stPressRobot.GetRobotFD(), stPressRobot.GetRobotUin())
            stPressRobot.RecvNetData()
            stPressRobot.ParseAndHandlerData()
    
    def RecvNetData(self):
        try:
            self.__recv_buff += self.__robot_sock.recv(65535)
        except Exception,e:
            print "Exception:%s, uin %u\n" %(e, self.GetRobotUin())
            return
    
    def ParseAndHandlerData(self):
        while(1):
            if(len(self.__recv_buff) < 2):
                return
            
            #首先解析2字节头
            iRecvMsgLen = socket.ntohs(struct.unpack("H", self.__recv_buff[:2])[0]) - 2
            if(len(self.__recv_buff[2:]) < iRecvMsgLen):
                #未收到1个完整的网络包，直接返回
                return 
            
            #尝试解析消息体
            RecvProtoMsg = CS_pb2.ProtocolCSMsg()
            
            RecvProtoMsg.ParseFromString(self.__recv_buff[2:(iRecvMsgLen+2)])
        
            self.__recv_buff = self.__recv_buff[(iRecvMsgLen+2):]
        
            self.RobotFunctionRun(RecvProtoMsg)
    
    def SendInitProtoData(self):
        raise RuntimeError("This function should be realized by child class!\n")

    def RobotFunctionRun(self, RecvProtoMsg):
        raise RuntimeError("This function should be realized by child class!\n");
    
    def GenerateMsgHead(self, stGameMsg, iMsgID):
        stGameMsg.m_stMsgHead.m_uiMsgID = iMsgID
        stGameMsg.m_stMsgHead.m_uin = self.__robot_uin
    
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
    
    