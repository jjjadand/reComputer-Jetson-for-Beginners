# SSH Remote Access

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## Introduction

SSH (Secure Shell) lets you log in to Jetson from another computer, run commands remotely, transfer files securely, and manage the system without a monitor or keyboard attached.

## Make Sure Jetson and Your PC Can Reach Each Other

The two devices must be on the same LAN unless you have routed or VPN access.

Check Jetson's IP address:

```bash
ip addr
```

or:

```bash
ifconfig
```

## Enable the SSH Service

Some images already include OpenSSH. If not, install and enable it:

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh
```

## Connect from Linux or macOS

```bash
ssh <username>@<jetson-ip>
```

Example:

```bash
ssh seeed@192.168.1.50
```

The first login asks you to confirm the host fingerprint. After that, enter the Jetson account password.

## Connect from Windows

You can use any SSH client, such as:

- Windows PowerShell
- Windows Terminal
- MobaXterm
- PuTTY

The connection format is the same:

```bash
ssh <username>@<jetson-ip>
```

## Ethernet Direct Connection

If Jetson cannot join Wi-Fi, you can connect it to a PC with an Ethernet cable and share the PC's network connection. After the link is up, inspect the wired interface IP on Jetson and connect to that address over SSH.

## Useful First Commands After Login

```bash
hostname
whoami
jtop
df -h
```

If `jtop` is not available, install it from [Jtop and System Monitoring](../3.16-Jtop-and-System-Monitoring/README.md).

## Troubleshooting

- If the connection times out, confirm both devices are on the same subnet.
- If you get `Connection refused`, make sure the `ssh` service is running.
- If the IP changed after reconnecting Wi-Fi, re-run `ip addr` on Jetson.

## Suggested Next Steps

- Use [Remote File Transfer](../3.15-Remote-File-Transfer/README.md) to copy datasets or scripts.
- Use [VS Code](../3.19-VS-Code/README.md) with the Remote - SSH extension for IDE-based development.

[Back to Module 3](../README.MD)
