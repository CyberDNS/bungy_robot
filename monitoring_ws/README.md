# Bungy Monitoring Workspace

This workspace provides visualization and monitoring tools for the Bungy Robot.

## Quick Start

```bash
# Build the monitoring workspace
cd ~/repos/bungy_robot
./build.sh monitoring

# Source and run monitoring
cd monitoring_ws
source setup.bash

# Launch basic monitoring
ros2 launch bungy_monitoring monitor_robot.launch.py

# OR launch with remote control
ros2 launch bungy_monitoring remote_monitor.launch.py robot_ip:=192.168.1.100
```

## What's Included

- **RVIZ2 configurations** for robot visualization
- **Remote teleoperation** via keyboard
- **RQT tools** for debugging and monitoring
- **Network communication** setup for multi-machine operation

## For complete documentation, see the main repository README.md