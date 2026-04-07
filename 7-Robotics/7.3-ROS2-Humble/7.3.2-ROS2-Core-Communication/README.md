# ROS2 Core Communication

This subchapter merges the node, topic, service, and action lessons from `xiaobai-lesson` Chapter 9 into one practical communication guide.

## Nodes

A ROS2 node is a process that uses the ROS2 client library to communicate with the rest of the graph. Good node design usually means:

- one clear responsibility per node
- descriptive node names
- low coupling through well-defined interfaces

Create a simple Python package and node:

```bash
cd ~/ros2_ws/src
ros2 pkg create pkg_helloworld_py --build-type ament_python --dependencies rclpy --node-name helloworld
```

Example node:

```python
import time
import rclpy
from rclpy.node import Node

class HelloWorldNode(Node):
    def __init__(self):
        super().__init__("helloworld")
        self.timer = self.create_timer(0.5, self.say_hello)

    def say_hello(self):
        self.get_logger().info("Hello World")

def main(args=None):
    rclpy.init(args=args)
    node = HelloWorldNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

Build and run:

```bash
cd ~/ros2_ws
colcon build --packages-select pkg_helloworld_py
source install/setup.bash
ros2 run pkg_helloworld_py helloworld
```

## Topics

Topics are used for stream-style communication. Publishers send messages to a named topic, and subscribers receive them without either side directly depending on the other's implementation.

Create a topic demo package:

```bash
cd ~/ros2_ws/src
ros2 pkg create pkg_topic --build-type ament_python --dependencies rclpy std_msgs --node-name publisher_demo
```

Publisher pattern:

```python
from std_msgs.msg import String

self.pub = self.create_publisher(String, "/topic_demo", 10)
self.timer = self.create_timer(1.0, self.publish_message)
```

Subscriber pattern:

```python
from std_msgs.msg import String

self.sub = self.create_subscription(String, "/topic_demo", self.callback, 10)
```

Useful commands:

```bash
ros2 topic list
ros2 topic echo /topic_demo
ros2 topic info /topic_demo
```

## Services

Services are synchronous request/response interactions. Use them for short operations like configuration, status queries, or one-shot calculations.

The source lesson used `example_interfaces/srv/AddTwoInts`.

Check the interface:

```bash
ros2 interface show example_interfaces/srv/AddTwoInts
```

Create a server:

```python
from example_interfaces.srv import AddTwoInts

self.srv = self.create_service(AddTwoInts, "/add_two_ints", self.handle_request)
```

Call it from the CLI:

```bash
ros2 service list
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 1, b: 4}"
```

The source material also demonstrated a Python client using `create_client()` and `call_async()`.

## Actions

Actions are for long-running tasks that need:

- progress feedback
- eventual result delivery
- optional cancellation

The merged source example defined a custom action:

```text
int64 num
---
int64 sum
---
float64 progress
```

Typical flow:

1. Create an interface package with the `.action` definition.
2. Build the interface package so generated code becomes available.
3. Create an action server package that processes the goal and publishes feedback.
4. Create an action client package that sends goals and receives progress updates.

Useful action commands:

```bash
ros2 action list
ros2 interface show pkg_interfaces/action/Progress
ros2 action send_goal /get_sum pkg_interfaces/action/Progress "{num: 10}"
```

## Choosing the Right Communication Type

| Need | Best Fit |
| --- | --- |
| Continuous sensor or state stream | Topic |
| Quick request/response operation | Service |
| Long task with progress and cancel support | Action |

## Practical Advice

- Keep message definitions stable once other packages depend on them.
- Prefer topics for data streams like camera images or detections.
- Prefer services for configuration changes or one-shot RPC style logic.
- Prefer actions for navigation, grasping, or long perception pipelines.

## Next Step

Continue with [ROS2 Advanced Interfaces and Middleware](../7.3.3-ROS2-Advanced-Interfaces-and-Middleware/README.md) to connect communication patterns to TF2, custom interfaces, parameters, DDS, and distributed ROS2 systems.
