# ROS2 Humble

This module merges the practical ROS2 content from `xiaobai-lesson` Chapter 9 into the `reComputer-Jetson-for-Beginners` structure. The original chapter covered setup, communication patterns, middleware, daily tooling, simulation, and vision-oriented demos. The content is now organized into five readable subchapters instead of a source-file index.

## What You Will Learn

- How to prepare a ROS2 Humble development environment on Jetson
- How ROS2 nodes, topics, services, actions, and TF2 fit together
- How to create packages, custom interfaces, and workspace layouts
- How to use `ros2` CLI tools, RViz2, RQt, launch files, and rosbag
- How URDF, Gazebo, camera preview, calibration, and AR demos connect to real robotics projects

## Module 7.3 Structure

| **Chapter** | **Content** |
|:-----------:|:------------|
| Module 7.3.1 | [ROS2 Foundations and Setup](./7.3.1-ROS2-Foundations-and-Setup/README.md) |
| Module 7.3.2 | [ROS2 Core Communication](./7.3.2-ROS2-Core-Communication/README.md) |
| Module 7.3.3 | [ROS2 Advanced Interfaces and Middleware](./7.3.3-ROS2-Advanced-Interfaces-and-Middleware/README.md) |
| Module 7.3.4 | [ROS2 Tools, Launch, and Visualization](./7.3.4-ROS2-Tools-Launch-and-Visualization/README.md) |
| Module 7.3.5 | [ROS2 Simulation and Vision](./7.3.5-ROS2-Simulation-and-Vision/README.md) |

## Source Coverage

The merged content covers the original lesson topics:

- ROS2 introduction, IDE setup, workspace, and package structure
- Nodes, topics, services, and actions
- TF2, custom interfaces, parameters, metapackages, distributed communication, DDS, and ROS time
- CLI tools, RViz2, RQt, launch files, and rosbag record/playback
- URDF, Gazebo, camera preview, camera calibration, and AR visual demos

## Suggested Flow

If you are new to ROS2 on Jetson, work through the subchapters in order. The first two establish the environment and communication model. The later chapters assume you can already build a workspace, source `install/setup.bash`, and run basic nodes.
