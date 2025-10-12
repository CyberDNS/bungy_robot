# Copilot Instructions for Bungy Robot

## Project Overview
Bungy Robot is a ROS 2 Jazzy differential drive robot running on Raspberry Pi 5 with Dynamixel AX-12A servos. The project follows a multi-workspace architecture designed for distributed deployment across robot and NUC hardware.

## Hardware Components
- **Raspberry Pi 5**: Main robot computer
- **Dynamixel AX-12A**: Differential drive servos with custom ros2_control interface
- **Slamtec RPLIDAR A1**: 2D 360° laser scanner
- **BNO055**: 9-DOF IMU sensor
- **INA219**: Current/power monitoring
- **WS2812**: RGB LED strips
- **Xbox One Controller**: Wireless teleoperation

## Architecture & Key Components

### Multi-Workspace Structure
- `core_ws/`: Shared dependencies workspace (built from `.repos` file)
- `robot_ws/`: Robot hardware workspace (runs on Raspberry Pi 5)
- `monitoring_ws/`: Visualization workspace (runs on NUC for monitoring robot/sim)
- `sim_ws/`: Simulation workspace (Gazebo simulation on NUC)
- `bungy_robot_description/`: Legacy Humble description (reference only, do not modify)

### Control Flow Architecture
```
Xbox Controller → joy_node → teleop_twist_joy → /cmd_vel (Twist)
                                                     ↓
twist_to_stamped_relay.py → /bungy/diff_cont/cmd_vel (TwistStamped)
                                                     ↓
                           ros2_control → Dynamixel Hardware
```

The **critical insight**: Standard teleop nodes publish `Twist` messages, but the diff_drive_controller expects `TwistStamped`. The `twist_to_stamped_relay.py` node bridges this gap.

## Build & Development Workflows

### Dependency Management
- Use `rosdep` for standard ROS dependencies where applicable
- Package-specific dependencies declared in respective `package.xml` files
- External/custom dependencies managed via `core_ws/.repos` file

### Package Building (robot_ws only)
```bash
cd robot_ws && colcon build --packages-select bungy_bringup && source ./setup.bash
```

### Core Dependencies Setup
```bash
cd core_ws && vcs import < ../bungy_robot.humble.repos && rosdep install --from-paths src -y
```

### Launch Patterns
- Robot only: `ros2 launch bungy_bringup robot.launch.py`
- With Xbox controller: `ros2 launch bungy_bringup robot_with_joystick.launch.py`
- Includes both robot.launch.py and joystick.launch.py via IncludeLaunchDescription

### Workspace-Specific Deployment
- **robot_ws**: Deploy to Raspberry Pi 5 for hardware control
- **monitoring_ws**: Run on NUC for visualization/monitoring
- **sim_ws**: Run on NUC for Gazebo simulation
- **core_ws**: Shared dependencies across all workspaces

### Package Conversion Pattern
This project underwent CMake→Python conversion for bungy_bringup:
- Moved scripts from `scripts/` to `bungy_bringup/` package directory
- Entry points in setup.py: `'twist_to_stamped_relay = bungy_bringup.twist_to_stamped_relay:main'`
- Launch files reference entry point names, not .py filenames

## Configuration Patterns

### Controller Configuration (`config/controllers.yaml`)
- Namespace: `/bungy/` for all controllers
- Wheel calibration via radius multipliers (drift compensation)
- Update rate: 50Hz (reduced from 100Hz to handle Raspberry Pi performance)

### Hardware-Specific Patterns
- Dynamixel servos: Left wheel inverted=1, right wheel inverted=-1
- Wheel separation: 0.184m, radius: 0.06m
- Serial communication causes timing overruns (expected behavior)

## Topic & Message Patterns

### Standard Topic Flow
- Input: `/cmd_vel` (geometry_msgs/Twist)
- Output: `/bungy/diff_cont/cmd_vel` (geometry_msgs/TwistStamped)
- Joint states: `/bungy/joint_states`

### Xbox Controller Integration
- Deadzone: 0.1 (increased from default 0.05)
- Linear scale: 0.3 (reduced for finer control)
- Uses joy + teleop_twist_joy packages, not custom implementations

## Hardware Integration Patterns

### Sensor Integration
- **RPLIDAR A1**: 2D laser scanning for navigation/mapping
- **BNO055**: IMU for orientation and pose estimation
- **INA219**: Power monitoring for battery management
- **WS2812**: Status indication via RGB LED strips

### Hardware Communication
- Dynamixel servos use serial communication (USB/RS485 converter)
- All sensors integrated via standard ROS 2 drivers from rosdep where available
- Custom drivers for specialized hardware in core_ws dependencies

## Common Development Tasks

### Drift Calibration
Adjust wheel radius multipliers in controllers.yaml:
- Robot drifts left → increase `right_wheel_radius_multiplier: 1.03`
- Robot drifts right → increase `left_wheel_radius_multiplier: 1.03`

### Adding New Commands
When adding velocity commands, publish to `/cmd_vel` (Twist), not directly to diff_cont. The relay node handles conversion automatically.

### Debugging Hardware Communication
Check for "Overrun detected" warnings - these are normal due to Dynamixel serial latency on Raspberry Pi. Performance tuning focuses on update_rate rather than eliminating overruns.