# ROS2 Foundations and Setup

This subchapter merges the setup-oriented lessons from `xiaobai-lesson` Chapter 9 into a single onboarding path for ROS2 Humble on Jetson.

## ROS2 in One Paragraph

ROS2 is a robotics middleware stack rather than an operating system. It provides the communication layer, package layout, tooling, and runtime conventions that let sensor drivers, algorithms, and application nodes work together across one machine or many machines.

## Core Concepts

- A `node` is the basic executable unit in ROS2.
- A `topic` is used for stream-style publish/subscribe data.
- A `service` is used for request/response interactions.
- An `action` is used for long-running tasks with feedback and cancellation.
- A `workspace` is the directory tree where you store, build, and install packages.
- A `package` is the standard unit for code, configuration, launch files, and metadata.

## Install ROS2 Humble on Ubuntu 22.04

The original source index referenced an install lesson, but the markdown file is missing in the current workspace. For completeness, the standard Humble setup flow on Ubuntu 22.04 is:

```bash
sudo apt update
sudo apt install -y software-properties-common curl
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
  sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install -y ros-humble-desktop python3-colcon-common-extensions python3-rosdep
sudo rosdep init
rosdep update
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

Validate the install:

```bash
ros2 --help
printenv | grep ROS_DISTRO
```

## Recommended IDE Setup

The merged source strongly preferred VS Code for ROS2 work on Jetson.

Recommended extensions:

- `ms-iot.vscode-ros`
- `ms-vscode.cpptools`
- `ms-python.python`
- `ms-vscode.cmake-tools`
- `redhat.vscode-yaml`
- `redhat.vscode-xml`

Open a workspace with:

```bash
code ~/ros2_ws
```

If you want better C/C++ IntelliSense, generate compile commands during build:

```bash
cd ~/ros2_ws
colcon build --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

Then point VS Code at `build/compile_commands.json`.

## Create a ROS2 Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
tree -L 2
```

A typical workspace contains:

- `src/`: source packages tracked in version control
- `build/`: intermediate build products
- `install/`: installed executables, libraries, and setup scripts
- `log/`: build and test logs

Build the workspace:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

Useful `colcon` patterns:

```bash
colcon build --packages-select my_package
colcon build --packages-skip my_package
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Debug
colcon build --event-handlers console_direct+
```

## Create Packages

Create a C++ package:

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake --dependencies rclcpp std_msgs my_cpp_pkg
```

Create a Python package:

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python --dependencies rclpy std_msgs my_py_pkg
```

Common package files:

- `package.xml`: metadata and dependencies
- `CMakeLists.txt`: C++ build rules for `ament_cmake`
- `setup.py` and `setup.cfg`: Python packaging for `ament_python`
- `launch/`: launch files
- `config/`: YAML and runtime config
- `resource/`: package resource marker

## `package.xml` Basics

The source chapter spent time on metadata and dependency types. A minimal package file usually contains:

```xml
<package format="3">
  <name>my_package</name>
  <version>0.0.1</version>
  <description>Example ROS2 package</description>
  <maintainer email="user@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <depend>rclcpp</depend>
  <depend>std_msgs</depend>
</package>
```

## Practical Advice on Jetson

- Keep one clean workspace for learning examples and another for your real project.
- Add `source ~/ros2_ws/install/setup.bash` only after the workspace is stable.
- Use `--symlink-install` during development so Python files update without a full reinstall.
- When a package fails to build, rebuild it alone first with `--packages-select`.

## Next Step

Continue with [ROS2 Core Communication](../7.3.2-ROS2-Core-Communication/README.md) once you can create a package, build a workspace, and source the resulting environment.
