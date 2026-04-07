# ROS2 Advanced Interfaces and Middleware

This subchapter merges the interface, TF2, parameter, middleware, and distributed-communication material from `xiaobai-lesson` Chapter 9.

## TF2 Coordinate Transforms

TF2 manages relationships between coordinate frames like `map`, `odom`, `base_link`, `camera_link`, and `laser_link`. It is the standard way to express where sensors and robot bodies are relative to one another.

Common TF2 uses:

- sensor fusion
- visualization in RViz2
- navigation frame management
- robot-arm end-effector pose calculation

Useful tools:

```bash
ros2 run tf2_ros tf2_echo turtle2 turtle1
ros2 run rqt_tf_tree rqt_tf_tree
rviz2
```

Static transforms are useful when two frames never move relative to each other:

```bash
ros2 run tf2_ros static_transform_publisher 0 0 0.3 0 0 0 base_link camera_link
```

## Custom Interfaces

The source lesson emphasized that topics, services, and actions all rely on formal interface definitions.

Create a custom message:

```text
string name
int32 age
float64 height
```

Create a custom service:

```text
int32 num1
int32 num2
---
int32 sum
```

Create a custom action:

```text
int64 num
---
int64 sum
---
float64 progress
```

Register them in `CMakeLists.txt`:

```cmake
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Person.msg"
  "srv/Add.srv"
  "action/Progress.action"
)
```

Then rebuild and inspect:

```bash
cd ~/ros2_ws
colcon build --packages-select pkg_interfaces
source install/setup.bash
ros2 interface show pkg_interfaces/msg/Person
ros2 interface show pkg_interfaces/srv/Add
ros2 interface show pkg_interfaces/action/Progress
```

## Parameters

ROS2 parameters are named runtime values attached to nodes. They are useful for tuning without hard-coding constants.

Inspect parameters:

```bash
ros2 param list
ros2 param describe turtlesim background_b
ros2 param get turtlesim background_b
ros2 param set turtlesim background_b 10
```

Save and reload parameters:

```bash
ros2 param dump turtlesim > turtlesim.yaml
ros2 param load turtlesim turtlesim.yaml
```

## Metapackages

The original source described metapackages as an installation and grouping layer for a set of related packages. A metapackage does not usually contain nodes itself. Instead, it declares execution dependencies so users can install or track one logical bundle.

Use them when you want to publish a module made of multiple packages, such as:

- robot bringup stacks
- navigation bundles
- lesson collections and demos

## Distributed Communication and DDS

ROS2 uses DDS as the transport layer under the hood. That gives ROS2:

- peer-to-peer discovery
- QoS controls
- multi-machine communication
- multiple DDS vendor implementations

For multi-machine work:

- keep devices on the same network segment when possible
- use the same `ROS_DOMAIN_ID`
- verify that firewalls are not blocking discovery traffic

Check your domain:

```bash
echo $ROS_DOMAIN_ID
export ROS_DOMAIN_ID=10
```

## ROS2 Time APIs

The source lesson grouped time APIs with middleware because they affect playback, simulation, and synchronization.

Typical time-related patterns:

- use node clocks instead of raw wall clock when simulation time matters
- distinguish wall time from ROS time
- use timers for periodic callbacks

Example:

```python
self.timer = self.create_timer(1.0, self.callback)
now = self.get_clock().now()
```

## Practical Advice

- Use TF2 early in a project instead of inventing your own transform bookkeeping.
- Put reusable interfaces in a dedicated `pkg_interfaces` style package.
- Treat parameters as public configuration, not as a hidden internal data bus.
- Understand QoS and DDS before debugging multi-camera or multi-machine systems.

## Next Step

Continue with [ROS2 Tools, Launch, and Visualization](../7.3.4-ROS2-Tools-Launch-and-Visualization/README.md) for the CLI, RViz2, RQt, launch files, and rosbag workflow that you will use every day.
