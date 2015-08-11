#!/bin/sh

./protoc --cpp_out=../../Src/proto/ GameProtocol.Common.proto || exit 1
./protoc --cpp_out=../../Src/proto/ GameProtocol.Account.proto || exit 1
./protoc --cpp_out=../../Src/proto/ GameProtocol.MsgID.proto || exit 1
./protoc --cpp_out=../../Src/proto/ GameProtocol.World.proto || exit 1
./protoc --cpp_out=../../Src/proto/ GameProtocol.CS.proto || exit 1
./protoc --cpp_out=../../Src/proto/ GameProtocol.Zone.proto || exit 1
./protoc --cpp_out=../../Src/proto/ GameProtocol.RegAuth.proto || exit 1

#记录的关键日志，用于对账
#./protoc --cpp_out=../../Src/proto/ ./GameProtocol.LOG.proto || exit 1

#后台DB数据存储的相关结构的定义
./protoc --cpp_out=../../Src/proto/ GameProtocol.USERDB.proto || exit 1
 
mv ../../Src/proto/GameProtocol.Common.pb.cc ../../Src/proto/GameProtocol.Common.pb.cpp
mv ../../Src/proto/GameProtocol.Account.pb.cc ../../Src/proto/GameProtocol.Account.pb.cpp
mv ../../Src/proto/GameProtocol.MsgID.pb.cc ../../Src/proto/GameProtocol.MsgID.pb.cpp
mv ../../Src/proto/GameProtocol.CS.pb.cc ../../Src/proto/GameProtocol.CS.pb.cpp
mv ../../Src/proto/GameProtocol.World.pb.cc ../../Src/proto/GameProtocol.World.pb.cpp
mv ../../Src/proto/GameProtocol.Zone.pb.cc ../../Src/proto/GameProtocol.Zone.pb.cpp
mv ../../Src/proto/GameProtocol.RegAuth.pb.cc ../../Src/proto/GameProtocol.RegAuth.pb.cpp

#记录的关键日志，用于对账
#mv ../../Src/proto/GameProtocol.LOG.pb.cc ../../Src/proto/GameProtocol.LOG.pb.cpp

#后台DB数据存储的相关结构的定义
mv ../../Src/proto/GameProtocol.USERDB.pb.cc ../../Src/proto/GameProtocol.USERDB.pb.cpp

echo "Success to Build all protocol"
