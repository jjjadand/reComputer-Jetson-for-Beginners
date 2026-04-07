# Linux Terminal and Text Editors

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## 01基础使用

本篇教程将介绍Linux系统的常用终端操作命令以及文本编辑工具的使用。

### 终端

Linux的终端（Terminal）是一个命令行界面，你可以通过它直接输入命令来操作系统，而不依赖图形界面。它可以用来管理文件、运行程序、安装软件、查看系统信息等，是Linux系统中非常核心的工具。简单来说，终端就是与系统“对话”的窗口。进入Jetson桌面后，键盘按下Cltr + Alt + T即可打开一个终端。

```
此外，还可以通过 SSH 远程打开 Jetson 设备的终端窗口。我们将在后续内容中详细介绍。
```

![](./images/3-11-linux-terminal-and-editors-01.png)

几乎所有能在图形界面上做的事情，都可以在终端里用命令完成，而且通常更高效、更直接。例如：基础文件操作、系统管理与监控、软件包管理、文件内容编辑等等。下面将介绍在终端中经常使用的命令。

### Linux基础命令

```bash
ls
```

![](./images/3-11-linux-terminal-and-editors-02.png)

```bash
mkdir test
# 创建多级文件夹
mkdir -p test/src
```

![](./images/3-11-linux-terminal-and-editors-03.png)

```bash
# cd + 目录路径
cd test/
# 返回上一级目录
cd ..
```

![](./images/3-11-linux-terminal-and-editors-04.png)

```bash
touch test.txt
```

![](./images/3-11-linux-terminal-and-editors-05.png)

```bash
pwd
```

![](./images/3-11-linux-terminal-and-editors-06.png)

```bash
# 删除文件
rm test.txt
# 删除文件夹 -rf 递归强制删除
rm -rf test/
```

![](./images/3-11-linux-terminal-and-editors-07.png)

```bash
clear
```

### 终端窗口中的快捷键

```
Ctrl + C
```

```
Tab
```

```
Ctrl + Z
```

鼠标选中终端文本,进行复制、粘贴

```
Ctrl + Shift + C
```

```
Ctrl + Shift + V
```

### 文本编辑工具

### Gedit

Gedit是Linux下的简单图形化文本编辑器，用于编辑代码和文本文件。有图像GUI。在终端窗口中输入下面的命令即可创建并打开一个文件：

```bash
# gedit + 文件名
gedit test.txt
```

![](./images/3-11-linux-terminal-and-editors-08.png)

### Nano

Nano是一款在终端中使用的轻量级文本编辑器，操作简便，适合快速编辑文件。无图形化的GUI：

```bash
# 安装nano
sudo apt update
sudo apt-get install nano -y
# 编辑文本
nano test.txt
```

![](./images/3-11-linux-terminal-and-editors-09.png)

### Vim/Vi

vi是Unix/Linux系统中最经典的命令行文本编辑器，从1976年开始就存在，是几乎所有Unix系统的标准编辑器。Vim是vi的增强版，兼容vi但功能更强大。

```bash
# 打开编辑页面
vim test.txt
```

```
进入编辑器后按i键才能进行文本编辑
```

![](./images/3-11-linux-terminal-and-editors-10.png)

```
编辑完成后，输入: 选择编辑模式进行下一步操作
常用模式命令：
保存文件
:w
退出
:q
保存并退出
:wq
强制退出不保存
:q!
强制保存并退出
:wq!
删除所有内容
:%d
查找文本 :/xxx xxx为查找的文本，按回车确认，按n进行下一个匹配到的条目的选择
```

![](./images/3-11-linux-terminal-and-editors-11.png)

## 14使用Vim编辑器

### Vim基础使用

Vim是Linux/Unix系统中常用的命令行文本编辑器，具有高效、轻量、无需鼠标即可完成编辑的特点，广泛用于服务器、嵌入式和开发环境。

在正式介绍Vim的基本使用之前，先说明Vim的工作模式，这是理解Vim操作的关键。

#### Vim的三种常用模式

### 1、打开文件

vim filename

### 2、进入插入模式

在普通模式下，键盘按下i

进入插入模式后即可输入文本。

### 3、退出插入模式

按下键盘的Esc返回普通模式。

### 4、保存与退出（命令模式）

在普通模式下键盘输入:进入命令模式：

### 5、常用光标移动（普通模式）

h左l右j下k上

### 6、删除操作（普通模式）

### 7、复制与粘贴（普通模式）

### 8、查找内容

查找内容可在键盘输入/关键字（关键字替换为你想查找的字符）

[Back to Module 3](../README.MD)
