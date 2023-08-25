#!/bin/bash

# Ask for the workspace name
read -p "Please enter the name for the new robot workspace (e.g., workspace/bungy): " robot_workspace_path

# Check if the directory already exists
if [ ! -d "$robot_workspace_path" ]; then
  echo "Workspace folder '$robot_workspace_path' does not exist. Getting code and dependecies..."


  # Path to the main robot repository
  robot_repo_path="$robot_workspace_path/src"

  # Create workspace directories
  mkdir -p "$robot_repo_path"

  robot_workspace_path=$(realpath -s $robot_workspace_path)
  robot_repo_path="$robot_workspace_path/src"

  echo "Robot workspace at '$robot_workspace_path' has been created successfully."

  # Installing prerequisites
  sudo bash -c '
  apt-get --assume-yes install ros-dev-tools ros-humble-gazebo-ros-pkgs ros-humble-joint-state-publisher-gui ros-humble-xacro \
              ros-humble-ros2-control ros-humble-ros2-controllers ros-humble-gazebo-ros2-control ros-humble-controller-manager \
              ros-humble-teleop-twist-keyboard ros-humble-teleop-twist-joy \
              joystick jstest-gtk evtest
  '


  # Clone the main robot repository
  echo "Cloning the main robot repository to '$robot_repo_path'..."
  git clone https://github.com/CyberDNS/bungy_robot.git "$robot_repo_path/bungy_robot"

  echo "Main robot repository has been cloned successfully."


  # Navigate to the robot src path
  cd "$robot_repo_path"

  # Execute the vcs import command to get the rest of the dependencies
  echo "Importing dependencies using vcs..."
  vcs import < ./bungy_robot/bungy_robot.humble.repos

  rm -rf "$robot_repo_path/dynamixel_sdk/.git/" 
  rm -rf "$robot_repo_path/dynamixel_sdk/dynamixel_sdk_examples/"

  echo "Dependencies have been successfully imported."
fi

# Generate the alias content based on the workspace name
alias_name="${robot_workspace_path##*/}"
alias_content="# Alias generated for robot workspace '$alias_name'\n"
alias_content+="alias _$alias_name='source /opt/ros/humble/setup.bash && source $robot_workspace_path/install/setup.bash'\n"
alias_content+="alias cb_$alias_name='colcon build --symlink-install --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON'\n"
alias_content+="alias cd_$alias_name='cd $robot_workspace_path'\n"
alias_content+="alias cds_$alias_name='cd $robot_workspace_path/src'\n"

# Create the alias file inside the workspace
alias_file_path="$robot_workspace_path/aliases.sh"
echo -e "$alias_content" > "$alias_file_path"

echo "Alias file has been generated at '$alias_file_path'."

# Check if the alias sourcing line is already in the .bashrc file
if ! grep -q "$alias_file_path" ~/.bashrc; then
    # Add sourcing of the alias file to the user's .bashrc
    echo -e "\n# Source the robot workspace alias file" >> ~/.bashrc
    echo "source $alias_file_path" >> ~/.bashrc
    echo "Alias sourcing has been added to ~/.bashrc."
else
    echo "Alias sourcing is already present in ~/.bashrc."
fi


# Navigate back to the robot workspace path
cd "$robot_workspace_path"

source /opt/ros/humble/setup.bash

# Execute the colcon build command
echo "Building the workspace using colcon build..."
colcon build --symlink-install --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON


echo "Workspace has been successfully built."
echo "Please restart your terminal session and source your new workspace"
echo "by typing: _$alias_name"

