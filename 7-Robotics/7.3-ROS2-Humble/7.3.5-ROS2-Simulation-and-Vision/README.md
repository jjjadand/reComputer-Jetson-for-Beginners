# ROS2 Simulation and Vision

This subchapter merges the modeling, simulation, camera, calibration, and AR perception lessons from `xiaobai-lesson` Chapter 9.

## URDF Modeling

URDF is the standard XML format used in ROS2 to describe a robot's links, joints, geometry, and inertial properties. It is the basis for:

- TF trees
- RViz robot visualization
- Gazebo simulation
- motion planning inputs

Key URDF concepts:

- `link`: a rigid body such as a chassis, wheel, arm segment, or sensor mount
- `joint`: the relationship between two links
- `visual`: how the link looks
- `collision`: simplified geometry for collision checking
- `inertial`: mass and inertia data

Common joint types from the merged source:

- `fixed`
- `continuous`
- `revolute`
- `prismatic`

## Gazebo

Gazebo is used to simulate robot motion, sensors, and physical interactions before moving to hardware.

Install ROS2 Gazebo integration:

```bash
sudo apt install ros-${ROS_DISTRO}-ros-gz
```

Bring up Gazebo through a launch file or integrated simulation package. Use it when you want to validate:

- robot bringup
- world interaction
- camera or lidar streams
- navigation and SLAM logic

## Camera Preview

The source material included a simple USB camera workflow.

Example launch step:

```bash
ros2 run camera camera_usb
```

View images with RQt:

```bash
rqt
```

Then open `Plugins -> Visualization -> Image View`.

The source also included a minimal OpenCV + `cv_bridge` publisher pattern for publishing `sensor_msgs/msg/Image`.

## Camera Calibration

Calibration estimates camera intrinsics and distortion coefficients so downstream vision tasks can work reliably.

Install the tool:

```bash
sudo apt install ros-humble-camera-calibration
```

Run calibration for an `8x6` checkerboard with `25 mm` squares:

```bash
ros2 run camera_calibration cameracalibrator --size 8x6 --square 0.025 \
  --ros-args --remap image:=/camera/color/image_raw --remap camera:=/camera/color
```

Best practices:

- move the board through different angles and distances
- fill most parts of the image over the full capture session
- save the resulting calibration file and keep it with the camera configuration

## AR Visual Demos

The source lesson used AR and chessboard-style pose-estimation examples to demonstrate augmented vision.

Dependencies mentioned in the original lesson:

```bash
sudo apt install ros-humble-vision-opencv
sudo apt install ros-humble-aruco-opencv
sudo apt install ros-humble-aruco_ros
pip3 install opencv-contrib-python
```

These demos are useful for:

- estimating marker pose
- aligning overlays to real scenes
- testing calibrated camera geometry
- building lightweight educational AR examples on Jetson

## Practical Advice

- Keep URDF collision geometry simpler than visual geometry.
- Validate TF and robot models in RViz2 before debugging Gazebo plugins.
- Calibrate cameras before trusting AR, stereo, or measurement tasks.
- Use simple USB-camera preview nodes first, then move to more complex perception stacks.
