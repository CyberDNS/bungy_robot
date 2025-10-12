#!/bin/bash

echo "=== Bungy Robot Workspace Structure ==="
echo ""
echo "All workspaces now follow standard ROS 2 structure:"
echo ""

cd /home/david/repos/bungy_robot

for ws in core_ws robot_ws monitoring_ws; do
    echo "📁 $ws/"
    echo "   ├── src/                  # Source packages"
    if [ -d "$ws/src" ]; then
        for pkg in $ws/src/*/; do
            if [ -d "$pkg" ]; then
                pkg_name=$(basename "$pkg")
                echo "   │   └── $pkg_name/"
            fi
        done
    fi
    echo "   ├── setup.bash           # Workspace setup script"
    echo "   ├── build/               # Build artifacts (auto-generated)"
    echo "   ├── install/             # Install artifacts (auto-generated)"
    echo "   └── log/                 # Build logs (auto-generated)"
    echo ""
done

echo "🔧 Setup Commands:"
echo "   Build all: ./build.sh"
echo "   Build specific: ./build.sh <workspace>"
echo "   Clean: ./build.sh <workspace> clean"
echo "   Help: ./build.sh --help"
echo "   Source workspace: cd <workspace> && source setup.bash"
echo ""

echo "📦 Package Purposes:"
echo "   bungy_description  → Robot URDF, shared across workspaces"
echo "   bungy_bringup     → Hardware control (Raspberry Pi)"
echo "   bungy_monitoring  → Visualization tools (NUC PC)"