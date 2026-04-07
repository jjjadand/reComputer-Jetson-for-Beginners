# VNC Remote Desktop

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## 04 VNC Remote Control

### Introduction

VNC is a remote desktop protocol that lets you view and control another device's graphical interface from your own computer. It is especially useful for servers without monitors, embedded devices such as Jetson, and other systems that require remote GUI access.

### Configure VNC

### Jetson side

Open desktop sharing on Jetson from `Settings -> Sharing`.

![](./images/3-14-vnc-remote-desktop-01.png)

Enable Remote Desktop, turn on the traditional VNC protocol, and set a username and password. Using the same credentials as the system account is recommended.

![](./images/3-14-vnc-remote-desktop-02.png)

![](./images/3-14-vnc-remote-desktop-03.png)

Each time you switch networks, make sure Media Sharing is still enabled.

![](./images/3-14-vnc-remote-desktop-04.png)

Enable remote login

![](./images/3-14-vnc-remote-desktop-05.png)

Enable the VNC service at boot.

If the screen is locked, VNC remote control may stop working. Use the extra configuration below to allow locked-screen remote access.

```bash
# Install the desktop extension manager
sudo apt install gnome-shell-extension-manager -y
# Get the gnome-shell version
gnome-shell --version
```

![](./images/3-14-vnc-remote-desktop-06.png)

Download the GNOME extension that allows remote desktop access while the screen is locked:

Open this page in a browser on the Jetson:

https://extensions.gnome.org/extension/4338/allow-locked-remote-desktop/

If no browser is installed, you can install a Firefox browser

```bash
# Download Firefox
sudo apt install firefox
#Fix the browser version
cd ~/Downloads/
snap download snapd --revision=24724
sudo snap ack snapd_24724.assert
sudo snap install snapd_24724.snap
sudo snap refresh --hold snapd
```

![](./images/3-14-vnc-remote-desktop-07.png)

Open the link above and download the extension version that matches your GNOME Shell version.

![](./images/3-14-vnc-remote-desktop-08.png)

Install the extension from the download directory:

```bash
gnome-extensions install allowlockedremotedesktopkamens.us.v9.shell-extension.zip
sudo gnome-extensions enable allowlockedremotedesktop@kamens.us
```

![](./images/3-14-vnc-remote-desktop-09.png)

Restart the system:

```bash
sudo reboot
```

After rebooting, press the `Win` key, search for `Extension Manager`, and enable the installed extension.

![](./images/3-14-vnc-remote-desktop-10.png)

![](./images/3-14-vnc-remote-desktop-11.png)

Turn on the option that allows remote desktop control while the screen is locked.

![](./images/3-14-vnc-remote-desktop-12.png)

### PC side

Download VNC Viewer

![](./images/3-14-vnc-remote-desktop-13.png)

Allow installation as administrator

![](./images/3-14-vnc-remote-desktop-14.png)

![](./images/3-14-vnc-remote-desktop-15.png)

![](./images/3-14-vnc-remote-desktop-16.png)

![](./images/3-14-vnc-remote-desktop-17.png)

![](./images/3-14-vnc-remote-desktop-18.png)

![](./images/3-14-vnc-remote-desktop-19.png)

![](./images/3-14-vnc-remote-desktop-20.png)

![](./images/3-14-vnc-remote-desktop-21.png)

Open VNC Viewer.

![](./images/3-14-vnc-remote-desktop-22.png)

Enter the Jetson IP address and press `Enter`.

![](./images/3-14-vnc-remote-desktop-23.png)

![](./images/3-14-vnc-remote-desktop-24.png)

Enter Jetson password

![](./images/3-14-vnc-remote-desktop-25.png)

The first connection may show a black screen.

![](./images/3-14-vnc-remote-desktop-26.png)

Adjust the viewer quality settings if needed.

![](./images/3-14-vnc-remote-desktop-27.png)

![](./images/3-14-vnc-remote-desktop-28.png)

At this point, you should be able to connect normally to the Jetson graphical desktop.

![](./images/3-14-vnc-remote-desktop-29.png)

[Back to Module 3](../README.MD)
