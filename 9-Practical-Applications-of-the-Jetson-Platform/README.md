# Practical Applications of the Jetson Platform

This module now merges the practical Isaac ROS content from `xiaobai-lesson` Chapter 10. The original source chapter was titled **NVIDIA Isaac ROS** and focused on Jetson-side quickstarts for GPU-accelerated robotics pipelines.

## What This Chapter Covers

- Preparing an Isaac ROS development environment on Jetson
- Understanding the Docker-based Isaac ROS workflow
- Running perception quickstarts for depth, segmentation, detection, pose estimation, and visual SLAM
- Understanding how these pipelines connect to navigation, manipulation, and 3D scene understanding
- A separate A-LOAM example for ROS1 users working with LiDAR SLAM

## Isaac ROS Environment Basics

The merged source assumes:

- JetPack 6.2
- Docker already installed on Jetson
- access to NVIDIA Isaac ROS development containers
- ROS2 Humble as the supported ROS version

Check whether relevant images are already present:

```bash
sudo docker images
```

A common Isaac ROS workspace pattern is:

```bash
export ISAAC_ROS_WS=~/isaac_ros-dev
mkdir -p ${ISAAC_ROS_WS}/src
cd ${ISAAC_ROS_WS}/src
git clone -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
cd isaac_ros_common
./scripts/run_dev.sh
```

The original source also noted that many quickstarts depend on assets hosted remotely, so network reliability matters during first-time setup.

## Core Isaac ROS Quickstarts

### Depth Segmentation

Used to estimate whether obstacles are present within a certain depth band.

Main quickstart fragment:

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py \
  launch_fragments:=bi3d \
  interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_bi3d/rosbag_quickstart_interface_specs.json \
  featnet_engine_file_path:=${ISAAC_ROS_WS}/isaac_ros_assets/models/bi3d_proximity_segmentation/featnet.plan \
  segnet_engine_file_path:=${ISAAC_ROS_WS}/isaac_ros_assets/models/bi3d_proximity_segmentation/segnet.plan \
  max_disparity_values:=10
```

### DNN Stereo Depth

Used for dense stereo depth inference in manipulation and perception stacks.

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py \
  launch_fragments:=ess_disparity \
  engine_file_path:=${ISAAC_ROS_WS}/isaac_ros_assets/models/dnn_stereo_disparity/dnn_stereo_disparity_v4.1.0_onnx/ess.engine \
  threshold:=0.0
```

### Free Space Segmentation

Used to estimate traversable ground space for navigation.

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py \
  launch_fragments:=bi3d,bi3d_freespace \
  interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_bi3d_freespace/rosbag_quickstart_interface_specs.json \
  featnet_engine_file_path:=${ISAAC_ROS_WS}/isaac_ros_assets/models/bi3d_proximity_segmentation/featnet.plan \
  segnet_engine_file_path:=${ISAAC_ROS_WS}/isaac_ros_assets/models/bi3d_proximity_segmentation/segnet.plan \
  max_disparity_values:=10
```

### Image Pipeline Operations

The source lesson grouped resize, color conversion, crop, and rectify under image-preprocessing workflows. These are typically brought up through `isaac_ros_examples` launch fragments such as:

- `resize`
- `color_conversion`
- `crop`
- `rectify_mono`

These operations are useful when camera outputs need to match model input size, format, or calibration requirements.

### Semantic Image Segmentation

The merged source used SegFormer:

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py \
  launch_fragments:=segformer \
  interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_segformer/quickstart_interface_specs.json \
  model_name:=peoplesemsegformer \
  model_repository_paths:=[${ISAAC_ROS_WS}/isaac_ros_assets/models]
```

### 3D Scene Reconstruction and Mapping

The source lesson used `nvblox` for real-time 3D reconstruction and navigation cost maps:

```bash
ros2 launch nvblox_examples_bringup isaac_sim_example.launch.py \
  rosbag:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_nvblox/quickstart \
  navigation:=False
```

### Object Detection

The merged source used DetectNet as the quickstart:

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py \
  launch_fragments:=detectnet \
  interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_detectnet/quickstart_interface_specs.json
```

### 3D Pose Estimation

The source lesson used CenterPose:

```bash
ros2 launch isaac_ros_examples isaac_ros_examples.launch.py \
  launch_fragments:=centerpose,centerpose_visualizer \
  interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_centerpose/quickstart_interface_specs.json \
  model_name:=centerpose_shoe \
  model_repository_paths:=[${ISAAC_ROS_WS}/isaac_ros_assets/models]
```

### Visual SLAM

Visual SLAM provides stereo-camera-based odometry and mapping:

```bash
rviz2 -d $(ros2 pkg prefix isaac_ros_visual_slam --share)/rviz/default.cfg.rviz

ros2 launch isaac_ros_examples isaac_ros_examples.launch.py \
  launch_fragments:=visual_slam \
  interface_specs_file:=${ISAAC_ROS_WS}/isaac_ros_assets/isaac_ros_visual_slam/quickstart_interface_specs.json \
  rectified_images:=false
```

## Common Pattern Across These Quickstarts

Most of the source examples follow the same structure:

1. Enter the Isaac ROS dev container with `run_dev.sh`.
2. Launch a pipeline.
3. Open another shell and play a sample rosbag.
4. Open a visualizer such as `rviz2`, `image_view`, or a package-specific visualization script.

Once you understand that loop, you can move much faster across Isaac ROS repositories.

## A-LOAM Bonus Workflow

The original Chapter 10 also included a ROS1-based A-LOAM lesson for RoboSense RS32 LiDAR. That workflow is separate from the Isaac ROS ROS2 content, but it is still useful if you are maintaining older ROS1 stacks or testing laser SLAM on Jetson.

Highlights from the merged source:

- install `libgflags-dev`, `libgoogle-glog-dev`, `libsuitesparse-dev`, `libpcl-dev`
- build `ceres-solver`
- clone `A-LOAM` into `~/catkin_ws/src`
- adapt topic names and point-cloud formats to match the LiDAR driver
- build with `catkin_make`

## Practical Advice

- Keep Isaac ROS work inside the dev container unless you have a strong reason not to.
- Expect first-run setup to pull large assets and engine files.
- Use sample rosbags first, then move to a real camera or robot once the pipeline is stable.
- Match each fragment to a concrete robotics use case: navigation, perception, mapping, or manipulation.
