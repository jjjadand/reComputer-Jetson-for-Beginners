# Practical Applications of the Jetson Platform

## 第十章Nvidia Isaac ROS

## 01环境搭建

### Isaac ROS环境搭建

```
注：SEEED部分出厂镜像已经配置好环境，无需自己搭建，可以跳过此步骤
```

你可以在jetson上运行下面指令查看系统是否预装Isaac ROS：

```bash
sudo docker images
```

![](./images/9-practical-applications-of-the-jetson-platform-01.png)

### Isaac ROS环境简介

Isaac ROS套件由NVIDIA开发并发布，旨在利用NVIDIA Jetson和独立GPU上的NVIDIA加速功能，开发标准的机器人应用程序。

Isaac ROS在输入和输出方面使用标准ROS接口，因此非常易于上手，可以作为机器人开发者所熟悉的常用CPU ROS实现的直接替代品。

### 系统要求

![](./images/9-practical-applications-of-the-jetson-platform-02.gif)

#### 点击图片可查看完整电子表格

### 适配的ROS版本

所有Isaac ROS软件包均经过设计和测试，与ROS 2 Humble兼容。

如果使用 是ROS 1 Noetic构建的，可以使用Isaac ROS NITROS Bridge集成Isaac ROS软件包，以获得更快的性能。（本节目前只以ROS2为例）

Isaac ROS软件包仅针对ROS 2 Humble进行了测试。其他ROS 2版本尚不支持。

```
注意：安装失败属于正常情况，安装此环境需要挂代理后才可以正常安装，挂代理的方法需要自行到网上搜。
```

### 快速安装

1.确认你的系统已经安装了jertpack6.2的系统，并将系统电源调成MAXN SUPER模式

![](./images/9-practical-applications-of-the-jetson-platform-03.png)

2.安装基础docker

```
安装dcoker与使用可以回顾：13 安装 Docker与基础使用
```

首先Add Docker's official GPG key:

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

然后Add the repository to Apt sources:

```bash
echo \
"deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt install docker-buildx-plugin
```

3.添加docker用户组

```bash
sudo usermod -aG docker $USER
newgrp docker
```

然后Add Jetson public APT repository

```sql
sudo apt-get update
sudo apt-get install software-properties-common
sudo apt-key adv --fetch-key https://repo.download.nvidia.com/jetson/jetson-ota-public.asc
sudo add-apt-repository 'deb https://repo.download.nvidia.com/jetson/common r36.4 main'
sudo apt-get update
sudo apt-get install -y pva-allow-2
```

5.设置开发环境

在${ISAAC_ROS_WS}/src下克隆isaac_ros_common。

```bash
cd ${ISAAC_ROS_WS}/src && \
git clone -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git isaac_ros_common
```

6.使用run_dev.sh脚本启动Docker容器：

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && ./scripts/run_dev.sh
```

等待docker拉取成功就搭建好了环境。

```
Isaac ROS的docker镜像需要认证 NVIDIA 的 NGC（NVIDIA GPU Cloud），否则镜像会拉不下来。
```

```
需要登录 NVIDIA NGC查看api key，使用的是：NGC API Key（不是 GitHub key）
```

终端输入docker login nvcr.io进行登录

#### 用户名：$oauthtoken

#### 密码：你的NGC API Key

## 02深度分割

```
dcoker的使用指令参考可以回顾： 13 安装 Docker与基础使用
```

Isaac ROS深度分割官网链接：https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_depth_segmentation/index.html

### 概述

Isaac ROS深度分割提供了NVIDIA加速的深度分割软件包。isaac_ros_bi3d软件包使用优化的Bi3D DNN模型，通过二值化进行立体深度估计，并用于深度分割。深度分割可用于确定障碍物是否位于邻近区域内，并避免在导航过程中与障碍物发生碰撞。

![](./images/9-practical-applications-of-the-jetson-platform-04.png)

Bi3D用于节点图，从时间同步的输入左右立体图像对中进行深度分割。Bi3D图像需要校正并调整大小以适应合适的输入分辨率。图像的宽高比需要保持；因此，可能需要裁剪和调整大小以保持输入宽高比。DNN编码、DNN推理和DNN解码的图是Bi3D节点的一部分。推理使用TensorRT执行，因为Bi3D DNN模型旨在使用TensorRT支持的优化。

与其他立体视差函数相比，深度分割可以预测障碍物是否位于邻近区域（而非连续深度），同时预测距离地面的自由空间，而其他函数通常无法提供此功能。此外，与Isaac ROS中的其他立体视差函数不同，深度分割在NVIDIA DLA（深度学习加速器）上运行，该加速器独立于GPU。

### 快速体验

为了简化开发，我们主要使用Isaac ROS Dev Docker镜像，并在上面进行效果演示。演示不需要安装任何摄像头设备，通过播放rosbag文件模拟来自摄像头的数据流。

注：如果想要安装在自己设备上，或者连接摄像头开发其他功能，请参照Isaac ROS官网，连接英伟达指定的摄像头型号自行开发。

打开终端进入工作目录

```bash
cd ${ISAAC_ROS_WS}/src
进入 Isaac ROS Dev Docke容器
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```
注意：拉取官方示例可能需要科学上网，请确保您的网络环境能够正常访问GitHub
```

```bash
cd /workspaces/isaac_ros-dev/src
# 例子仓库（提供 isaac_ros_examples.launch.py 等 quickstart launch）
git clone -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_examples.git
# bi3d 所在仓库（Depth Segmentation / Bi3D）
git clone -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_depth_segmentation.git
# 通用工具仓库（run_dev、脚本、一些通用依赖/配置）
git clone -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
cd /workspaces/isaac_ros-dev
# 确保 rosdep 可用（dev 容器一般已具备）
sudo apt-get update
rosdep update
# 安装工作空间依赖
rosdep install --from-paths src --ignore-src -r -y
# 编译
colcon build --symlink-install
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py \
launch_fragments:=bi3d \
interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_bi3d/rosbag_quickstart_interface_specs.json \
featnet_engine_file_path:=${ISAAC_ROS_WS}/isaac_ros_assets/models/bi3d_proximity_segmentation/featnet.plan \
segnet_engine_file_path:=${ISAAC_ROS_WS}/isaac_ros_assets/models/bi3d_proximity_segmentation/segnet.plan \
max_disparity_values:=10
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play --loop ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_bi3d/bi3dnode_rosbag
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令，查看深度分割图

```bash
ros2 run isaac_ros_bi3d isaac_ros_bi3d_visualizer.py --max_disparity_value 30
```

![](./images/9-practical-applications-of-the-jetson-platform-05.png)

打开第四个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令，查看图像

```bash
ros2 run image_view image_view --ros-args -r image:=right/image_rect
```

![](./images/9-practical-applications-of-the-jetson-platform-06.png)

## 03 DNN立体深度

```
dcoker的使用指令参考可以回顾： 13 安装 Docker与基础使用
```

Isaac ROS DNN立体深度官网链接：https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_dnn_stereo_depth/index.html

### 概述

视觉深度感知问题在机器人的许多领域都具有普遍的应用，例如在物体操作任务中估计机械臂的姿态、在自主机器人导航中估计静态或移动目标的距离、在送货机器人中跟踪目标等等。Isaac ROS DNN Stereo Depth针对两个Isaac应用程序，即Isaac Manipulator和Isaac Perceptor。在Isaac Manipulator应用程序中，ESS作为插件节点部署在Isaac ROS cuMotion包中，为机械臂运动规划和控制提供深度感知图。在此场景中，将执行桌面任务的工业机械臂的多摄像机立体流传递给ESS以获得相应的深度流。深度流用于分割机械臂与桌面上相应物体的相对距离；从而提供用于避免碰撞和细粒度控制的信号。同样，Isaac Perceptor应用程序使用了几个Isaac ROS包，即Isaac ROS Nova、Isaac ROS Visual Slam、Isaac ROS Stereo Depth (ESS)、Isaac ROS Nvblox和Isaac ROS Image Pipeline。

![](./images/9-practical-applications-of-the-jetson-platform-07.png)

### 快速体验

为了简化开发，我们主要使用Isaac ROS Dev Docker镜像，并在上面进行效果演示。演示不需要安装任何摄像头设备，通过播放rosbag文件模拟来自摄像头的数据流。

注：如果想要安装在自己设备上，或者连接摄像头开发其他功能，请参照Isaac ROS官网，连接英伟达指定型号的摄像头自行开发。

打开终端进入工作目录

```bash
cd ${ISAAC_ROS_WS}/src
进入 Isaac ROS Dev Docke容器
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令，其中threshold:=0.0在启动时可以修改成0.4，将会有不同的效果。

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=ess_disparity \
engine_file_path:=${ISAAC_ROS_WS:?}/isaac_ros_assets/models/dnn_stereo_disparity/dnn_stereo_disparity_v4.1.0_onnx/ess.engine \
threshold:=0.0
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play -l ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_ess/rosbags/ess_rosbag \
--remap /left/camera_info:=/left/camera_info_rect /right/camera_info:=/right/camera_info_rect
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令：

```bash
ros2 run isaac_ros_ess isaac_ros_ess_visualizer.py
```

当threshold设置成0.0时,显示结果如下:

![](./images/9-practical-applications-of-the-jetson-platform-08.png)

、

当threshold设置成0.4时,显示结果如下:

![](./images/9-practical-applications-of-the-jetson-platform-09.png)

## 04自由空间分段

```
dcoker的使用指令参考可以回顾： 13 安装 Docker与基础使用
```

Isaac ROS自由空间分段官网链接：https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_freespace_segmentation/index.html

### 概述

Isaac ROS自由空间分割包含一个ROS 2软件包，用于生成导航的占用网格。Bi3D自由空间通过处理包含机器人相对于地面姿态的自由空间分割掩码，为Nav2生成占用网格，用于在导航过程中避开障碍物。该软件包采用GPU加速，可在机器人应用中提供实时、低延迟的结果。Bi3D自由空间为移动机器人（地面机器人）提供了额外的占用网格源。

![](./images/9-practical-applications-of-the-jetson-platform-10.png)

### 快速体验

为了简化开发，我们主要使用Isaac ROS Dev Docker镜像，并在上面进行效果演示。演示不需要安装任何摄像头设备，通过播放rosbag文件模拟来自摄像头的数据流。

注：如果想要安装在自己设备上，或者连接摄像头开发其他功能，请参照Isaac ROS官网，连接英伟达指定型号的摄像头自行开发。

打开终端进入工作目录，进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令，

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py \
launch_fragments:=bi3d,bi3d_freespace \
interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_bi3d_freespace/rosbag_quickstart_interface_specs.json \
featnet_engine_file_path:=${ISAAC_ROS_WS}/isaac_ros_assets/models/bi3d_proximity_segmentation/featnet.plan \
segnet_engine_file_path:=${ISAAC_ROS_WS}/isaac_ros_assets/models/bi3d_proximity_segmentation/segnet.plan \
max_disparity_values:=10
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play -l ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_bi3d_freespace/quickstart.bag
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令，查看结果

```bash
rviz2
```

![](./images/9-practical-applications-of-the-jetson-platform-11.png)

## 05图像畸变处理

```
dcoker的使用指令参考可以回顾： 13 安装 Docker与基础使用
```

Isaac ROS图像畸变处理：https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_image_pipeline/index.html

### 概述

Isaac ROS图像畸变处理使用是的Isaac ROS图像管道，这是一个图像处理功能的元包。相机输出通常需要预处理，以满足多种不同感知功能的输入要求。这包括裁剪、调整大小、镜像、校正镜头畸变以及色彩空间转换。对于立体相机，需要进行额外的处理，以产生左右图像与点云之间的视差，从而实现深度感知。

![](./images/9-practical-applications-of-the-jetson-platform-12.png)

### 快速体验

为了简化开发，我们主要使用Isaac ROS Dev Docker镜像，并在上面进行效果演示。演示不需要安装任何摄像头设备，通过播放rosbag文件模拟来自摄像头的数据流。

注：如果想要安装在自己设备上，或者连接摄像头开发其他功能，请参照Isaac ROS官网，连接英伟达指定型号的摄像头自行开发。

#### Resize:

打开终端进入工作目录，进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=resize
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play --loop ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_image_proc/quickstart --remap /hawk_0_left_rgb_image:=/image_raw /hawk_0_left_rgb_camera_info:=/camera_info
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 run image_view image_view --ros-args --remap image:=resize/image
```

![](./images/9-practical-applications-of-the-jetson-platform-13.png)

### Color Conversion:

打开终端进入工作目录

注：如果已经开启过容器运行过其他命令，请在第一个终端输入exit退出所有docker容器后再运行命令。

打开终端进入工作目录，并进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令：

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=color_conversion interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_image_proc/quickstart_interface_specs.json
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令：

```bash
ros2 bag play --loop ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_image_proc/quickstart --remap /hawk_0_left_rgb_image:=/image_raw /hawk_0_left_rgb_camera_info:=/camera_info
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 run image_view image_view --ros-args --remap image:=image_mono
```

![](./images/9-practical-applications-of-the-jetson-platform-14.png)

### Crop:

打开终端进入工作目录，并进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=crop interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_image_proc/quickstart_interface_specs.json
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play --loop ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_image_proc/quickstart --remap /hawk_0_left_rgb_image:=/image_raw /hawk_0_left_rgb_camera_info:=/camera_info
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 run image_view image_view --ros-args --remap image:=crop/image
```

![](./images/9-practical-applications-of-the-jetson-platform-15.png)

### Rectify:

打开终端进入工作目录并进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=rectify_mono interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_image_proc/quickstart_interface_specs.json
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play --loop ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_image_proc/quickstart --remap /hawk_0_left_rgb_image:=/image_raw /hawk_0_left_rgb_camera_info:=/camera_info
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 run image_view image_view --ros-args --remap image:=image_rect
```

![](./images/9-practical-applications-of-the-jetson-platform-16.png)

### Flip:

打开终端进入工作目录并进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=flip
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play --loop ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_image_proc/quickstart --remap /hawk_0_left_rgb_image:=/image_raw /hawk_0_left_rgb_camera_info:=/camera_info
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 run image_view image_view --ros-args --remap image:=image_flipped
```

![](./images/9-practical-applications-of-the-jetson-platform-17.png)

## 06图像分割

```
dcoker的使用指令参考可以回顾： 13 安装 Docker与基础使用
```

Isaac ROS图像分割官网链接：https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_image_segmentation/index.html

### 概述

Isaac ROS图像分割包含用于语义图像分割的ROS软件包。

这些软件包通过在DNN模型上运行GPU加速推理，提供对输入图像进行像素级分类的方法。输入图像的每个像素都被预测属于一组定义的类别。感知函数可以使用输出预测来理解每个类别在二维图像中的空间位置，或将其与三维场景中相应的深度位置融合。

![](./images/9-practical-applications-of-the-jetson-platform-18.png)

### 快速体验

为了简化开发，我们主要使用Isaac ROS Dev Docker镜像，并在上面进行效果演示。演示不需要安装任何摄像头设备，通过播放rosbag文件模拟来自摄像头的数据流。

注：如果想要安装在自己设备上，或者连接摄像头开发其他功能，请参照Isaac ROS官网，连接英伟达指定的摄像头型号自行开发。

打开终端进入工作目录并进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=segformer interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_segformer/quickstart_interface_specs.json model_name:=peoplesemsegformer model_repository_paths:=[${ISAAC_ROS_WS}/isaac_ros_assets/models]
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play -l isaac_ros_assets/isaac_ros_segformer/segformer_sample_data
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令，查看结果

```bash
ros2 run rqt_image_view rqt_image_view /segformer/colored_segmentation_mask
```

![](./images/9-practical-applications-of-the-jetson-platform-19.png)

## 07 3D场景重建和映射

```
dcoker的使用指令参考可以回顾： 13 安装 Docker与基础使用
```

Isaac ROS 3D场景重建和映射官网链接：https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_nvblox/index.html

### 概述

Isaac ROS Nvblox包含用于导航的3D重建和代价地图的ROS 2软件包。isaac_ros_nvblox处理深度和姿态数据，实时重建3D场景，并输出用于Nav2的2D代价地图。代价地图用于导航规划，作为一种基于视觉的解决方案来规避障碍物。

isaac_ros_nvblox旨在与深度摄像头和/或3D激光雷达配合使用。该软件包利用GPU加速，使用独立于底层框架的C++库nvblox来计算3D重建和2D代价地图。

![](./images/9-practical-applications-of-the-jetson-platform-20.png)

### 快速体验

为了简化开发，我们主要使用Isaac ROS Dev Docker镜像，并在上面进行效果演示。演示不需要安装任何摄像头设备，通过播放rosbag文件模拟来自摄像头的数据流。

注：如果想要安装在自己设备上，或者连接摄像头开发其他功能，请参照Isaac ROS官网，连接英伟达指定的摄像头型号自行开发。

打开终端进入工作目录并进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```bash
ros2 launch nvblox_examples_bringup isaac_sim_example.launch.py \
rosbag:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_nvblox/quickstart \
navigation:=False
```

运行结果

![](./images/9-practical-applications-of-the-jetson-platform-21.png)

## 08对象检测

```
dcoker的使用指令参考可以回顾： 13 安装 Docker与基础使用
```

Isaac ROS对象检测官网链接：https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_object_detection/index.html

### 概述

Isaac ROS物体检测包含ROS 2中用于执行物体检测的软件包。isaac_ros_rtdetr、isaac_ros_detectnet和isaac_ros_yolov8分别提供了一种使用边界框对输入图像进行空间分类的方法。分类由相应架构的GPU加速模型执行：

isaac_ros_rtdetr：RT-DETR模型

isaac_ros_detectnet：DetectNet模型

isaac_ros_yolov8：YOLOv8模型

输出预测可供感知函数用来理解图像中物体的存在及其空间位置。

![](./images/9-practical-applications-of-the-jetson-platform-22.png)

### 快速体验

为了简化开发，我们主要使用Isaac ROS Dev Docker镜像，并在上面进行效果演示。演示不需要安装任何摄像头设备，通过播放rosbag文件模拟来自摄像头的数据流。

注：如果想要安装在自己设备上，或者连接摄像头开发其他功能，请参照Isaac ROS官网，连接英伟达指定的摄像头型号自行开发。

打开终端进入工作目录并进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=detectnet interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_detectnet/quickstart_interface_specs.json
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play -l ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_detectnet/rosbags/detectnet_rosbag --remap image:=image_rect camera_info:=camera_info_rect
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 run isaac_ros_detectnet isaac_ros_detectnet_visualizer.py --ros-args --remap image:=detectnet_encoder/resize/image
```

打开第四个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令，查看结果

```bash
ros2 run rqt_image_view rqt_image_view /detectnet_processed_image
```

![](./images/9-practical-applications-of-the-jetson-platform-23.png)

## 09 3D姿态估计

```
dcoker的使用指令参考可以回顾： 13 安装 Docker与基础使用
```

Isaac ROS 3D姿态估计官网链接：https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_pose_estimation/isaac_ros_centerpose/index.html

### 概述

Isaac ROS姿态估计包含三个ROS 2包，用于预测物体的姿态。请参考下表了解它们之间的区别：

![](./images/9-practical-applications-of-the-jetson-platform-24.gif)

#### 点击图片可查看完整电子表格

这些软件包使用GPU加速进行DNN推理，以估计物体的姿态。感知函数可以使用输出预测与相应的深度融合，从而提供物体的3D姿态和距离，以便进行导航或操作。

![](./images/9-practical-applications-of-the-jetson-platform-25.png)

### 快速体验

为了简化开发，我们主要使用Isaac ROS Dev Docker镜像，并在上面进行效果演示。演示不需要安装任何摄像头设备，通过播放rosbag文件模拟来自摄像头的数据流。

注：如果想要安装在自己设备上，或者连接摄像头开发其他功能，请参照Isaac ROS官网，连接英伟达指定的摄像头型号自行开发。

打开终端进入工作目录并进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=centerpose,centerpose_visualizer interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_centerpose/quickstart_interface_specs.json model_name:=centerpose_shoe model_repository_paths:=[${ISAAC_ROS_WS}/isaac_ros_assets/models]
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 bag play -l ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_centerpose/quickstart.bag
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令，查看结果

```bash
ros2 run rqt_image_view rqt_image_view /centerpose/image_visualized
```

![](./images/9-practical-applications-of-the-jetson-platform-26.png)

## 10视觉SLAM

```
dcoker的使用指令参考可以回顾： 13 安装 Docker与基础使用
```

Isaac ROS视觉SLAM官网链接：https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_visual_slam/index.html

### 概述

Isaac ROS Visual SLAM为VSLAM（视觉同步定位与地图构建）提供了一个高性能、一流的ROS 2软件包。该软件包使用一个或多个立体摄像头以及可选的IMU来估算里程，并将其作为导航的输入。它采用GPU加速，可在机器人应用中提供实时、低延迟的结果。VSLAM为移动机器人（地面）提供了额外的里程计源，并且可以作为无人机的主要里程计源。

![](./images/9-practical-applications-of-the-jetson-platform-27.png)

### 快速体验

为了简化开发，我们主要使用Isaac ROS Dev Docker镜像，并在上面进行效果演示。演示不需要安装任何摄像头设备，通过播放rosbag文件模拟来自摄像头的数据流。

注：如果想要安装在自己设备上，或者连接摄像头开发其他功能，请参照Isaac ROS官网，连接英伟达指定的摄像头型号自行开发。

打开终端进入工作目录并进入Isaac ROS Dev Docke容器

```bash
cd ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行下面启动命令

```bash
rviz2 -d $(ros2 pkg prefix isaac_ros_visual_slam --share)/rviz/default.cfg.rviz
```

打开第二个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py launch_fragments:=visual_slam \
interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_visual_slam/quickstart_interface_specs.json \
rectified_images:=false
```

#### 查看运行结果

打开第三个终端，进入容器

```bash
cd ${ISAAC_ROS_WS}/src/isaac_ros_common && \
./scripts/run_dev.sh
```

运行以下命令，可以看到rviz2显示。如果没有出现图像，可以再次运行这个命令。

```bash
ros2 bag play ${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_visual_slam/quickstart_bag --remap \
/front_stereo_camera/left/image_raw:=/left/image_rect \
/front_stereo_camera/left/camera_info:=/left/camera_info_rect \
/front_stereo_camera/right/image_raw:=/right/image_rect \
/front_stereo_camera/right/camera_info:=/right/camera_info_rect \
/back_stereo_camera/left/image_raw:=/rear_left/image_rect \
/back_stereo_camera/left/camera_info:=/rear_left/camera_info_rect \
/back_stereo_camera/right/image_raw:=/rear_right/image_rect \
/back_stereo_camera/right/camera_info:=/rear_right/camera_info_rect
```

![](./images/9-practical-applications-of-the-jetson-platform-28.png)

## 01如何在Jetson上运行A-LOAM 3D SLAM

### A-LOAM简介

A-LOAM是由J. Zhang和S. Singh提出的原始LOAM（实时激光雷达里程计与建图）算法的高级实现。A-LOAM的主要特点包括：

A-LOAM可用于自动驾驶、机器人和3D建图等多种应用。

本文档提供了在reComputer Jetson系列上使用RoboSense RS32 LiDAR传感器设置并运行A-LOAM（高级LOAM）算法的详细步骤。A-LOAM是LOAM的高级实现，利用Eigen和Ceres Solver实现高效的实时建图与定位。

![](./images/9-practical-applications-of-the-jetson-platform-29.gif)

### 前置条件

```
下面的内容仅在 Ubuntu 20.04 和 ROS Noetic 上进行了测试。请参考 8.01.01 ROS1 简介 完成 ROS 环境设置。
```

```
请参考这里安装 RoboSense RS32 LiDAR 的 SDK。
```

### 开始使用

### 环境设置

在Jetson的终端中执行下面的步骤。

```bash
sudo apt-get install libgflags-dev libgoogle-glog-dev
sudo apt-get install libsuitesparse-dev libcxsparse3 libcxsparse-dev
```

```bash
sudo apt install libpcl-dev
```

```bash
wget ceres-solver.org/ceres-solver-1.14.0.tar.gz
tar xvf ceres-solver-1.14.0.tar.gz
cd ceres-solver-1.14.0
mkdir build
cd build
cmake ..
make -j4
sudo make install
```

```bash
cd ~/catkin_ws/src
git clone https://github.com/HKUST-Aerial-Robotics/A-LOAM.git
```

### 修改配置文件

![](./images/9-practical-applications-of-the-jetson-platform-30.png)

![](./images/9-practical-applications-of-the-jetson-platform-31.png)

![](./images/9-practical-applications-of-the-jetson-platform-32.png)

```
C++
# include <opencv/cv.h>
```

```
C++
# include <opencv2/opencv.hpp>
```

![](./images/9-practical-applications-of-the-jetson-platform-33.png)

![](./images/9-practical-applications-of-the-jetson-platform-34.png)

![](./images/9-practical-applications-of-the-jetson-platform-35.png)

### 编译包

```bash
cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
```

### 启动3D SLAM

```bash
roslaunch rslidar_sdk start.launch
```

```bash
roslaunch aloam_velodyne aloam_velodyne_HDL_32.launch
```

![](./images/9-practical-applications-of-the-jetson-platform-36.png)
