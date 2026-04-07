# VNC Remote Desktop

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## 04 VNC远程控制

### 介绍

VNC（Virtual Network Computing）是一种远程桌面协议，可以让你在自己的电脑上看到另一台设备的图形界面，并像本地一样操作鼠标和键盘。通过VNC，你可以远程打开软件、查看桌面、管理系统，特别适合在没有显示器的服务器、嵌入式设备（如Jetson）或远程电脑上进行图形化操作。

### 配置VNC

### Jetson端

进入Jetson开启桌面远程共享，设置——>Sharing

![](./images/3-14-vnc-remote-desktop-01.png)

将远程桌面打开，启用传统VNC协议，设置用户名和密码(建议和系统保持一致)

![](./images/3-14-vnc-remote-desktop-02.png)

![](./images/3-14-vnc-remote-desktop-03.png)

每次切换网络都要检查Media Sharing是否打开

![](./images/3-14-vnc-remote-desktop-04.png)

开启远程登录

![](./images/3-14-vnc-remote-desktop-05.png)

开机自启动VNC服务

Jetson主板锁屏后无法进行VNC远程，需要以下额外配置

```bash
# 安装桌面拓展管理
sudo apt install gnome-shell-extension-manager -y
# 获取gnome-shell版本号
gnome-shell --version
```

![](./images/3-14-vnc-remote-desktop-06.png)

根据版本号下载允许锁屏下远程的插件：

在Jetson浏览器中打开:

https://extensions.gnome.org/extension/4338/allow-locked-remote-desktop/

如果没有安装浏览器，可以安装火狐浏览器

```bash
# 下载火狐浏览器
sudo apt install firefox
# 版本修复浏览器
cd ~/Downloads/
snap download snapd --revision=24724
sudo snap ack snapd_24724.assert
sudo snap install snapd_24724.snap
sudo snap refresh --hold snapd
```

![](./images/3-14-vnc-remote-desktop-07.png)

在浏览器打开上面的链接，选择对应的版本号自动下载

![](./images/3-14-vnc-remote-desktop-08.png)

进入插件下载目录安装插件

```bash
gnome-extensions install allowlockedremotedesktopkamens.us.v9.shell-extension.zip
sudo gnome-extensions enable allowlockedremotedesktop@kamens.us
```

![](./images/3-14-vnc-remote-desktop-09.png)

重启系统

```bash
sudo reboot
```

重启进入桌面，按win键，搜索Extension Manager。开启对应功能。

![](./images/3-14-vnc-remote-desktop-10.png)

![](./images/3-14-vnc-remote-desktop-11.png)

打开允许锁屏进行远程桌面控制

![](./images/3-14-vnc-remote-desktop-12.png)

### PC端

下载VNC Viewer

![](./images/3-14-vnc-remote-desktop-13.png)

以管理员身份允许安装程序

![](./images/3-14-vnc-remote-desktop-14.png)

![](./images/3-14-vnc-remote-desktop-15.png)

![](./images/3-14-vnc-remote-desktop-16.png)

![](./images/3-14-vnc-remote-desktop-17.png)

![](./images/3-14-vnc-remote-desktop-18.png)

![](./images/3-14-vnc-remote-desktop-19.png)

![](./images/3-14-vnc-remote-desktop-20.png)

![](./images/3-14-vnc-remote-desktop-21.png)

打开VNC Viewer软件

![](./images/3-14-vnc-remote-desktop-22.png)

输入Jetson IP地址回车

![](./images/3-14-vnc-remote-desktop-23.png)

![](./images/3-14-vnc-remote-desktop-24.png)

输入Jetson密码

![](./images/3-14-vnc-remote-desktop-25.png)

第一次打开可能会黑屏

![](./images/3-14-vnc-remote-desktop-26.png)

设置一下远程桌面的画质即可

![](./images/3-14-vnc-remote-desktop-27.png)

![](./images/3-14-vnc-remote-desktop-28.png)

至此可以正常远程连接Jetson的图形化界面了

![](./images/3-14-vnc-remote-desktop-29.png)

[Back to Module 3](../README.MD)
