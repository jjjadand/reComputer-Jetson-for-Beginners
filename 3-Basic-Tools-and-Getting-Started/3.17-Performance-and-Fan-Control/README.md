# Performance and Fan Control

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## 07 Turn on maximum performance mode

This section is the same as the 08 in Chapter II to start the Super Mode. Please move to the previous chapter to learn!

## 08 Manual control of fan rotation

### Introduction

On Jeton, there are two main ways to control the speed of fans manually: 1. Use the jtop tool. 2. Use terminal command line tools. However, on JetPack 6.2, the fan control was taken over entirely by Thermal Subsystem, which no longer provides user-written interfaces. Therefore, the following is only a demonstration of how to control the speed of a fan using a terminal command.

### Terminal command control

If you want to control the speed of a fan by script, or if jtop is not available, you can directly modify the PWM file at the bottom of the system.

> The speed conversion range of the fan is 0-255.

Set the fan full speed

Open the terminal to run the following commands:

```bash
# Stop the system fan service
sudo systemctl stop nvfancontrol.service
echo 255 | sudo tee /sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1
```

Close the fan

```bash
echo 0| sudo tee /sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1
```

> In JetPack 6.2, the othermal framework will automatically re-engineer the pwm value every second, and we set pwm to 0 to be maintained (because the othermal considers 0 to be closed, without trigger control), but the pwm set to 255 for one second only (hermal write back the default immediately) is mandatory at the system level! If you want a fan to keep moving at a certain speed, you can continue to write the desired value to the pwm1 file through scripts.

[Back to Module 3](../README.MD)
