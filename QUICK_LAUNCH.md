# 🚀 Quick Launch Scripts

These scripts automate the workflow for updating and launching the Bungy Robot system across distributed hardware.

## 📋 Scripts Overview

### `update_and_monitor.sh` - **For NUC/Monitoring Station**
Pulls latest code, builds core + monitoring workspaces, and launches RViz visualization.

**Usage:**
```bash
cd /path/to/bungy_robot
./update_and_monitor.sh
```

**What it does:**
- ✅ `git pull` latest changes  
- ✅ Build `core_ws` (shared dependencies)
- ✅ Build `monitoring_ws` (visualization)
- ✅ Launch RViz with EKF sensor fusion monitoring
- ✅ Set `ROS_DOMAIN_ID=42` for network isolation

### `update_and_launch_robot.sh` - **For Raspberry Pi/Robot**
Pulls latest code, builds core + robot workspaces, and launches the complete robot system.

**Usage:**
```bash
cd /path/to/bungy_robot  
./update_and_launch_robot.sh
```

**What it does:**
- ✅ `git pull` latest changes
- ✅ Build `core_ws` (shared dependencies)  
- ✅ Build `robot_ws` (robot control)
- ✅ Launch complete robot with all sensors
- ✅ Set `ROS_DOMAIN_ID=42` for network isolation

## 🔄 Typical Workflow

### 1. On Raspberry Pi (Robot):
```bash
./update_and_launch_robot.sh
```
Wait for all sensors to initialize (RPLIDAR, BNO055, controllers).

### 2. On NUC (Monitoring):
```bash  
./update_and_monitor.sh
```
RViz opens with:
- 🟢 Green arrows: EKF-filtered odometry (stable)
- 🔴 Red dots: LIDAR data (smaller, precise)
- 📊 Real-time sensor fusion monitoring

## 🌐 Network Setup

Both scripts automatically set `ROS_DOMAIN_ID=42` for:
- Network isolation from other ROS systems
- Clean communication between robot and monitoring station
- Consistent domain across distributed deployment

## 🛠️ Features Included

**Robot System:**
- Dynamixel AX-12A motor control
- RPLIDAR A1 2D laser scanning  
- BNO055 9-DOF IMU orientation
- EKF sensor fusion (IMU + wheel odometry)
- Xbox 360 controller teleoperation

**Monitoring System:**
- Real-time robot visualization
- EKF-corrected odometry display
- LIDAR environment mapping
- TF tree monitoring
- Sensor fusion diagnostics

## 📁 Workspace Architecture

```
bungy_robot/
├── core_ws/          # Shared dependencies (robot description, etc.)
├── robot_ws/         # Robot hardware control (Raspberry Pi)  
├── monitoring_ws/    # Visualization system (NUC)
└── *.sh             # Quick launch scripts
```

The distributed architecture allows:
- **Robot**: Lightweight hardware control on Raspberry Pi
- **Monitoring**: Resource-intensive visualization on NUC
- **Core**: Shared robot description and dependencies