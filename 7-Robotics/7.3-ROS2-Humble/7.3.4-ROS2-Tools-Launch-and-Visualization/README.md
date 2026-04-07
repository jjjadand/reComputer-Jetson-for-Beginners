# ROS2 Tools, Launch, and Visualization

This subchapter merges the day-to-day ROS2 tooling lessons from `xiaobai-lesson` Chapter 9.

## CLI Commands You Will Use Constantly

The original lesson on common tools focused on learning the graph through the command line. Start with these:

```bash
ros2 node list
ros2 node info /my_node
ros2 topic list
ros2 topic echo /my_topic
ros2 topic hz /my_topic
ros2 service list
ros2 action list
ros2 param list
ros2 interface list
```

A practical debugging loop on Jetson is often:

1. `ros2 node list`
2. `ros2 topic list`
3. `ros2 topic echo` or `ros2 topic hz`
4. `ros2 param list`
5. `rqt` or `rviz2` if visual inspection is needed

## RViz2

RViz2 is the standard visualization tool for TF, point clouds, images, robot models, markers, and more.

Launch it:

```bash
rviz2
```

Typical displays to add:

- `TF`
- `RobotModel`
- `Image`
- `LaserScan`
- `PointCloud2`
- `Marker`

Use RViz2 when you need to check:

- whether frames are connected correctly
- whether a robot model is valid
- whether sensors are publishing what you expect

## RQt

RQt is a plugin-based toolbox rather than a single feature. Useful plugins include:

- `rqt_graph`
- `rqt_tf_tree`
- `rqt_image_view`
- `rqt_plot`
- `rqt_reconfigure` where supported

Start it with:

```bash
rqt
```

The source lessons used `rqt_image_view` frequently for camera and perception examples.

## Launch Files

Launch files let you start multiple nodes with one command, pass arguments, and configure parameters in a repeatable way.

Run a launch file:

```bash
ros2 launch my_package my_launch.py
```

Example pattern:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package="demo_nodes_cpp", executable="talker", name="talker"),
        Node(package="demo_nodes_cpp", executable="listener", name="listener"),
    ])
```

Use launch files when:

- you need multiple nodes together
- a demo requires parameters or remaps
- you want a stable bringup command for a robot or tutorial

## Record and Playback with Rosbag

The source lesson called this "recordback"; in ROS2 the tool is `ros2 bag`.

Record all topics:

```bash
ros2 bag record -a
```

Record selected topics:

```bash
ros2 bag record /camera/image_raw /tf /odom
```

Inspect a bag:

```bash
ros2 bag info rosbag2_2026_02_09-17_20_58
```

Replay it:

```bash
ros2 bag play rosbag2_2026_02_09-17_20_58
```

Useful playback options:

```bash
ros2 bag play rosbag2_2026_02_09-17_20_58 -r 10
ros2 bag play rosbag2_2026_02_09-17_20_58 -l
ros2 bag play rosbag2_2026_02_09-17_20_58 --topics /chatter
```

## Practical Advice

- Use `ros2 topic echo` before assuming a node is broken.
- Keep a short rosbag sample when debugging perception or SLAM pipelines.
- Put stable demos behind launch files instead of long manual command chains.
- Use RViz2 for frame- and geometry-related debugging, and RQt for graph-level inspection.

## Next Step

Continue with [ROS2 Simulation and Vision](../7.3.5-ROS2-Simulation-and-Vision/README.md) to connect modeling, Gazebo, camera workflows, and AR examples into real robotics experiments.
