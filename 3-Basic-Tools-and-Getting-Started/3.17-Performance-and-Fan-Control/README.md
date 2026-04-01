# Performance and Fan Control

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## Introduction

Jetson platforms can trade power consumption for performance through `nvpmodel`, `jetson_clocks`, and thermal control. This page covers the common commands beginners use when they want the device to run at higher performance during AI workloads.

## Check Available Power Modes

Different Jetson modules expose different mode IDs, so inspect them first:

```bash
sudo nvpmodel -q --verbose
```

On some Seeed Jetson Orin Nano Super images, a high-performance mode may be available as:

```bash
sudo nvpmodel -m 2
```

> Note: The exact mode number is board- and image-dependent. Always verify the available modes on your device before changing it.

## Maximize Clock Frequency

After selecting the power mode, lock clocks to the highest supported level:

```bash
sudo jetson_clocks
```

Then open `jtop` to confirm the effect:

```bash
jtop
```

## Fan Control from the Command Line

On many Jetson devices the fan PWM value is exposed under:

```bash
/sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1
```

To stop the automatic fan service and force full speed:

```bash
sudo systemctl stop nvfancontrol.service
echo 255 | sudo tee /sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1
```

To stop the fan:

```bash
echo 0 | sudo tee /sys/devices/platform/pwm-fan/hwmon/hwmon0/pwm1
```

## Important JetPack 6.2 Note

On some JetPack 6.2 systems, the kernel thermal subsystem will quickly overwrite manual PWM settings. In practice this means:

- setting PWM to `0` may persist
- setting PWM to `255` may be reverted after about one second

If you need a persistent custom fan speed:

- prefer controlling it through `jtop` when supported, or
- run a service or script that rewrites the PWM value continuously, or
- keep the default thermal policy if stability matters more than manual tuning

## Safety Notes

- Do not stop the fan for long-running high-load workloads.
- Monitor temperature with `jtop` after every performance change.
- Benchmark only after power mode, clocks, and thermals are stable.

[Back to Module 3](../README.MD)
