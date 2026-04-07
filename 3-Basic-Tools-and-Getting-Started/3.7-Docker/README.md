# Docker on Jetson

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## 13安装Docker与基础使用

### 介绍

Docker是一款轻量级的容器化平台，用于将应用程序及其依赖打包成独立、可移植的容器，从而实现“在任何地方都能以相同方式运行”。它通过隔离环境、快速部署和高效资源利用，让开发、测试、部署流程更加一致和自动化。无论是本地开发、服务器部署，还是大规模微服务架构，Docker都能显著提升效率和稳定性。

### Jetson安装Docker服务

#### 安装Docker CE

```bash
sudo apt update
# 安装依赖
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
```

添加Docker官方GPG密钥：

```bash
# 添加阿里云 Docker 仓库 Key
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-ce.gpg
# 添加仓库
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-ce.gpg] \
https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
# 安装
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
# 验证安装
docker --version
```

![](./images/3-7-docker-01.png)

添加访问权限

```bash
sudo usermod -aG docker $USER
newgrp docker
```

执行以上命令后，就可以不需要使用sudo命令就可以直接使用docker命令

安装NVIDIA Container Toolkit

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
# 添加Key
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | \
sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
# 添加仓库
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
sed 's# deb https://# deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://# g' | \
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

![](./images/3-7-docker-02.png)

安装nvidia-container-toolkit

```bash
sudo apt update
sudo apt install -y nvidia-container-toolkit
```

启用Docker GPU支持

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
# 测试 Docker 容器内是否可使用 GPU
sudo docker run --rm --runtime=nvidia --gpus all --network host ubuntu nvidia-smi
```

```
下载 docker 镜像时可能需要科学上网！
```

如果你无法使用Docker官方APT仓库来安装Docker Engine，也可以选择手动下载.deb包并安装，参考下面流程。 👇👇👇

首先选择与你Ubuntu版本对应的仓库目录，打开Docker官方下载目录：

👉https://download.docker.com/linux/ubuntu/dists/

根据你当前使用的Ubuntu版本，选择对应的目录：

| Ubuntu 版本 | 版本代号 | 下载路径示例 |
| --- | --- | --- |
| Ubuntu 20.04 LTS | focal | dists/focal/pool/stable/ |
| Ubuntu 22.04 LTS | jammy | dists/jammy/pool/stable/ |
| Ubuntu 24.04 LTS | noble | dists/noble/pool/stable/ |

例如：

进入对应版本目录后，选择与你系统匹配的架构目录之一：

在对应架构目录中，下载以下5个deb文件（版本号建议保持一致）：

然后安装Docker（使用dpkg），进入你下载deb文件的目录，执行：

```bash
sudo dpkg -i ./containerd.io_<version>_<arch>.deb \
./docker-ce_<version>_<arch>.deb \
./docker-ce-cli_<version>_<arch>.deb \
./docker-buildx-plugin_<version>_<arch>.deb \
./docker-compose-plugin_<version>_<arch>.deb
```

如果提示依赖缺失，可以执行：

```bash
sudo apt -f install
```

如果需要验证Docker服务状态：

```bash
sudo systemctl status docker
```

Docker通常会在安装完成后自动启动。如果未启动，手动启动：

```bash
sudo systemctl start docker
```

### dcoker基础使用

Docker引擎包括Docker CLI，Docker CLI提供与Docker守护进程交互的命令行工具，教程介绍Docker常用命令的用法。

在正式介绍Docker的基本使用之前，我们先补充说明Docker中“镜像（Image）”和“容器（Container）”的基本概念，以帮助读者更好地理解后续内容。

简单来说：

```
镜像相当于程序的安装包，容器相当于正在运行的程序实例。
```

理解了镜像与容器的关系后，接下来将通过具体示例介绍Docker的常用命令和基本使用方法。

### 1、查看详细信息

```
docker info
```

### 2、查看版本号

```
docker --version
```

### 3、拉取镜像

```
docker pull <image_name>
```

若没有指定标签，默认会拉取latest标签的镜像。

手动拉取指定docker镜像：

```
docker pull <image_name>:<tag>
```

### 4、运行镜像

若本地没有需要运行的镜像，docker会自动拉取对应镜像。

```
docker run <image_name>
```

从指定镜像启动容器：

```
docker run ubuntu:18.04 /bin/bash
```

这会以交互模式启动，当输入exit退出（退出前如果没有保存，操作会清空）

#### 4.1、查看正运行的容器

```
docker ps
```

#### 4.2、查看正运行或停止容器

```
docker ps -a
```

### 5、清理容器

```
docker container prune
```

### 6、查看本地镜像

```
docker images
```

### 7、删除镜像

注意：待删除的镜像需要处于停止运行且被清理的状态

```
docker rmi <image_name>
```

### 8、保存容器为新的镜像

```
docker commit <container_id> <image_name>:<tag>
```

注意：根据实际的CONTAINER ID以及自定义的镜像名称和tag后缀

### 9、停止容器

若是以交互模式运行容器，且终端进入容器内部，可以在容器内部输入exit停止容器；

若是在外部关闭容器，可以使用docker stop命令。

```
docker stop
```

注意：根据实际CONTAINER ID进行修改

### 10、多终端进同一容器

容器之间是相互隔离的，直接使用运行镜像的命令会启动不同容器；若需要在同一容器执行操作，需要使用命令进入同一容器。

以交互模式从ubuntu:18.04镜像中启动一个容器：

docker run -it ubuntu:18.04 /bin/bash

然后，查看正在运行的容器：

docker ps

记录容器ID后，可从另一个终端进入相同的容器，例如：

docker exec -it bc4fcf3ef267 /bin/bash

根据实际情况，bc4fcf3ef267改为你使用的容器ID

[Back to Module 3](../README.MD)
