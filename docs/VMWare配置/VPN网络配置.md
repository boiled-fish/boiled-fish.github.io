一、系统环境
主机系统：win10
虚拟机系统：Ubuntu 20.04
VPN：clash for windows

二、Clash for Windows设置
在windows主机上，确保Clash for Windows的VPN是有效的状态
1. 在主页面，找到”Allow LAN“（允许局域网连接）选项并勾选
2. 记录代理端口：默认是7890
3. 保持“System Proxy”（系统代理）处于关闭状态 （虚拟机需要直接连接到Clash的代理端口，而非通过windows系统代理）

同时需要把windows网络适配器的VMNet8的ip设置为静态ip，避免动态分配ip影响ubuntu代理ip对应错误

三、Ubuntu虚拟机设置
在系统内配置之前，首先要配置虚拟机的网络适配器：
1. 保持虚拟机关闭（在虚拟机运行时修改网络配置，可能导致配置信息无法正确保存，造成配置混乱。在虚拟机运行时修改网络配置，可能会导致端口占用状态不一致，影响后续的网络连接）
2. 进入对应虚拟机的Settings
3. 选择”Network Adapter“（网络适配器），并确认已勾选”Connected”（已连接）和“Connect at power on”（启动时连接）
4. 选择网络连接模式为NAT（配置简单）
5. 点击“Advanced”，确保已启用“Generate a MAC address”（生成mac地址），已生成的话则不需要再生成（避免网络冲突）

四、Ubuntu系统设置
1. 在系统设置中的“Network”中，选择“Network Proxy”，选择“Manul”手动
	在HTTP、HTTPS、FTP、SOCKS字段中，输入主机上虚拟网卡的ip地址
	一般是 VMWare Network Adapter VMnet8的IPv4地址
	端口号使用Clash的代理端口

2. 需要配置 /etc/apt/apt.conf.d/proxy.conf 文件
	如果这个文件不存在，则vim新建一个即可
	内容是：
	``` shell
	Acquire::http::Proxy "http://ip:7890";
	Acquire::https::Proxy "http://ip:7890";
	```

3. 需要配置 ~/.bashrc
	在该文件内添加配置
	``` shell
	export http_proxy="http://ip:port"
	export https_proxy="http://ip:port"
	```
	更新后，需要source 一下来使其生效
	```shell
	source ~/.bashrc
	```

4. 配置Git使用代理
	```shell
	git config --global http.proxy "http://ip:port"
	git config --global https.proxy "http://ip:port"
	```