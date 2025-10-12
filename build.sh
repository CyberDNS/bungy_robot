#!/bin/bash

# Bungy Robot Multi-Workspace Build Script
# Usage: ./build.sh [workspace] [action]

set -e  # Exit on any error

# Color codes for output  
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

show_usage() {
    echo "Bungy Robot Build Script"
    echo ""
    echo "Usage: $0 [workspace] [action]"
    echo ""
    echo "Workspaces:"
    echo "  core        - Build core_ws (bungy_description)"
    echo "  robot       - Build robot_ws (bungy_bringup)"  
    echo "  monitoring  - Build monitoring_ws (bungy_monitoring)"
    echo "  all         - Build all workspaces (default)"
    echo ""
    echo "Actions:"
    echo "  build       - Build workspace(s) (default)"
    echo "  clean       - Clean workspace(s)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Build all workspaces"
    echo "  $0 core              # Build only core_ws"
    echo "  $0 robot clean       # Clean only robot_ws"
    echo "  $0 all clean         # Clean all workspaces"
}

# Parse arguments
if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_usage
    exit 0
fi

WORKSPACE=${1:-all}
ACTION=${2:-build}

print_status "Bungy Robot Build System"
echo "Workspace: $WORKSPACE" 
echo "Action: $ACTION"
echo ""

# Change to repo root
cd "$(dirname "$0")"

# Source ROS2 environment
if [ -f "/opt/ros/jazzy/setup.bash" ]; then
    source /opt/ros/jazzy/setup.bash
    print_status "Sourced ROS 2 Jazzy environment"
else
    print_error "ROS 2 Jazzy not found! Please install ROS 2 Jazzy first."
    exit 1
fi

if [ "$ACTION" = "clean" ]; then
    if [ "$WORKSPACE" = "all" ]; then
        for ws in core robot monitoring; do
            if [ -d "${ws}_ws" ]; then
                print_status "Cleaning ${ws}_ws..."
                cd "${ws}_ws" && rm -rf build/ install/ log/ && cd ..
                print_success "${ws}_ws cleaned"
            fi
        done
    else
        if [ -d "${WORKSPACE}_ws" ]; then
            print_status "Cleaning ${WORKSPACE}_ws..."
            cd "${WORKSPACE}_ws" && rm -rf build/ install/ log/ && cd ..
            print_success "${WORKSPACE}_ws cleaned"
        fi
    fi
elif [ "$ACTION" = "build" ]; then
    if [ "$WORKSPACE" = "all" ]; then
        # Build core first (dependency)
        print_status "Building core_ws (bungy_description)..."
        cd core_ws && colcon build --packages-select bungy_description && cd ..
        print_success "core_ws built"
        
        # Build robot_ws
        print_status "Building robot_ws (bungy_bringup)..."  
        cd robot_ws && colcon build --packages-select bungy_bringup && cd ..
        print_success "robot_ws built"
        
        # Build monitoring_ws
        print_status "Building monitoring_ws (bungy_monitoring)..."
        cd monitoring_ws && colcon build --packages-select bungy_monitoring && cd ..
        print_success "monitoring_ws built"
        
        print_success "All workspaces built successfully!"
    else
        case $WORKSPACE in
            "core") 
                print_status "Building core_ws..."
                cd core_ws && colcon build --packages-select bungy_description && cd ..
                ;;
            "robot")
                print_status "Building robot_ws..."
                # Source core_ws first for dependencies
                if [ -f "core_ws/install/setup.bash" ]; then
                    source core_ws/install/setup.bash
                fi
                cd robot_ws && colcon build --packages-select bungy_bringup && cd ..
                ;;
            "monitoring")
                print_status "Building monitoring_ws..."
                # Source core_ws first for dependencies  
                if [ -f "core_ws/install/setup.bash" ]; then
                    source core_ws/install/setup.bash
                fi
                cd monitoring_ws && colcon build --packages-select bungy_monitoring && cd ..
                ;;
            *)
                print_error "Unknown workspace: $WORKSPACE"
                show_usage
                exit 1
                ;;
        esac
        print_success "${WORKSPACE}_ws built successfully!"
    fi
else
    print_error "Unknown action: $ACTION"
    show_usage
    exit 1
fi
