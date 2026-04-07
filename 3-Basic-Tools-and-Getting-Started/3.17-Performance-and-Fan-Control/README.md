# Performance and Fan Control

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## 07开启最大性能模式

本篇内容与第二章中的08启动Super模式内容相同，请移步到前面章节学习！

## 08手动控制风扇转速

### 介绍

在Jeton上，手动控制风扇转速的方式主要有两种: 1.使用jtop工具。2.使用终端命令行工具。但在JetPack 6.2上，风扇控制完全由内核的Thermal Subsystem接管，不再提供用户可写接口。所以，以下只演示如何使用终端命令控制风扇转速。

### 终端命令控制

如果你想通过脚本控制风扇的转速，或者jtop无法使用，可以直接修改系统底层的PWM(脉冲宽度调制)文件。

```
风扇的转速数值设置范围是0-255（0停止，255全速）
```

#### 设置风扇全速

打开终端运行以下命令:

```bash
# 停止系统风扇服务
sudo systemctl stop nvfancontrol.service
echo 255 | sudo tee /sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1
```

#### 关闭风扇

```bash
echo 0| sudo tee /sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1
```

```
在 JetPack 6.2 中 thermal framework 会自动调速，每秒刷新 pwm 值，我们将pwm 设置为 0 可以保持（因为 thermal 认为 0 是关闭，不触发控制），但 pwm 设置为 255 只持续一秒（thermal 立刻写回默认值）这是系统级的强制行为！如果你希望风扇可以保持一定的转速持续运行，可以通过脚本持续向pwm1文件中写入期望的值。
```

[Back to Module 3](../README.MD)
