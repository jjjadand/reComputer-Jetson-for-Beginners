# VNC Remote Desktop

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## Introduction

VNC (Virtual Network Computing) lets you control the Jetson desktop remotely from another computer. It is useful when you need a graphical session for browser setup, IDE usage, or desktop debugging.

> Note: VNC is best suited to desktop sessions where Jetson is already logged in. For headless remote desktop scenarios, [NoMachine](../3.10-Nomachine/README.md) is often easier to keep stable.

## Enable Desktop Sharing on Jetson

On the Jetson desktop:

1. Open `Settings`.
2. Open `Sharing`.
3. Enable desktop sharing or remote desktop.
4. Enable remote login if the image provides that option.
5. Set a username and password for remote access.

After changing networks, re-check that sharing is still enabled.

## Install a VNC Client on Your PC

Common clients include:

- RealVNC Viewer
- TigerVNC Viewer

After installation:

1. Enter the Jetson IP address.
2. Confirm the connection.
3. Enter the VNC password.

## Lock-Screen and Headless Notes

On some Jetson desktop images, remote control stops working after the screen locks. In that case:

- disable automatic screen lock for development sessions, or
- use a GNOME extension that allows locked remote desktop sessions, or
- switch to [NoMachine](../3.10-Nomachine/README.md) for headless access

If you use the GNOME extension workflow, the common steps are:

```bash
sudo apt update
sudo apt install -y gnome-shell-extension-manager firefox
gnome-shell --version
```

Then download a version-compatible extension such as `Allow Locked Remote Desktop`, install it, reboot, and enable it from Extension Manager.

## Troubleshooting

- If the connection is black or very slow, lower the image quality in the VNC client.
- If you cannot connect after Wi-Fi changes, verify the current Jetson IP address again.
- If Jetson is fully headless and VNC is unreliable, use [NoMachine](../3.10-Nomachine/README.md).

## Visual Walkthrough

The VNC screenshots extracted during the merge are embedded here so the setup flow can be followed directly from the lesson page.

<details>
<summary>VNC desktop setup screenshots</summary>

![Open Jetson settings](./images/04-vnc-remote-desktop-01.png)
![Go to sharing](./images/04-vnc-remote-desktop-02.png)
![Enable remote desktop](./images/04-vnc-remote-desktop-03.png)
![Enable the VNC-compatible option](./images/04-vnc-remote-desktop-04.png)
![Set credentials for remote access](./images/04-vnc-remote-desktop-05.png)
![Enable remote login](./images/04-vnc-remote-desktop-06.png)
![Install the extension manager](./images/04-vnc-remote-desktop-07.png)
![Check the GNOME version](./images/04-vnc-remote-desktop-08.png)
![Open the browser download page](./images/04-vnc-remote-desktop-09.png)
![Download the lock-screen extension](./images/04-vnc-remote-desktop-10.png)
![Install the extension package](./images/04-vnc-remote-desktop-11.png)
![Enable the extension from the terminal](./images/04-vnc-remote-desktop-12.png)
![Reboot the system](./images/04-vnc-remote-desktop-13.png)
![Open Extension Manager](./images/04-vnc-remote-desktop-14.png)
![Enable locked remote desktop](./images/04-vnc-remote-desktop-15.png)
![Confirm the extension is active](./images/04-vnc-remote-desktop-16.png)
![Install VNC Viewer on the PC](./images/04-vnc-remote-desktop-17.png)
![Launch the viewer as administrator if needed](./images/04-vnc-remote-desktop-18.png)
![Accept the installation flow](./images/04-vnc-remote-desktop-19.png)
![Open the VNC client](./images/04-vnc-remote-desktop-20.png)
![Enter the Jetson IP address](./images/04-vnc-remote-desktop-21.png)
![Confirm the connection warning](./images/04-vnc-remote-desktop-22.png)
![Enter the VNC password](./images/04-vnc-remote-desktop-23.png)
![First remote desktop attempt](./images/04-vnc-remote-desktop-24.png)
![Adjust image quality if needed](./images/04-vnc-remote-desktop-25.png)
![Tune the viewer settings](./images/04-vnc-remote-desktop-26.png)
![Reconnect with the new settings](./images/04-vnc-remote-desktop-27.png)
![Normal remote desktop session](./images/04-vnc-remote-desktop-28.png)
![Jetson desktop controlled from the PC](./images/04-vnc-remote-desktop-29.png)

</details>

[Back to Module 3](../README.MD)
