发版说明文档：

1、客户端发布：
	客户端只发布测试包，包命名格式为： 包类型_日期_小版本号.apk
	包类型为： 内网测试、外网测试；
	日期格式为: 20190126
	小版本号为： 1天内有多个版本，从01、02往后一直增加；

2、服务端发布：
	1、程序更新so、Config.zip、proto、lua;
	2、策划更新 server\lua\award_1_42004_xdbyconfig.lua, 从ConfigTool\server_lua中复制过来即可；
	3、策划根据更新房间需求，配置 server\Config.json 中的so房间列表，为levelid 1,2,3；
	4、策划执行更新工具 DeployServer.exe, 输出中没有报错则更新成功；
	