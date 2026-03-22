#!/bin/bash
# =============================================================================
# Rosmaster X3 Plus — Workstation Environment Setup
# Source this file: source ~/Workspaces/x3_plus/setup_env.bash
# =============================================================================

# ROS2 Humble base
source /opt/ros/humble/setup.bash

# Domain ID — must match the robot (default 0 means all ROS2 on the network see each other)
export ROS_DOMAIN_ID=42

# Use Cyclone DDS for reliable multi-machine communication
# (FastRTPS works but Cyclone is generally more reliable across machines)
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Cyclone DDS config for reliable multi-machine discovery
export CYCLONEDDS_URI=file://$HOME/Workspaces/x3_plus/cyclonedds.xml

# Tell ROS2 this is the workstation (useful in launch files)
export ROBOT_NAME="rosmaster_x3"
export ROS_MACHINE="workstation"

# Source the local workspace overlay (if built)
if [ -f ~/Workspaces/x3_plus/install/setup.bash ]; then
    source ~/Workspaces/x3_plus/install/setup.bash
fi

echo "[X3 Plus] Workstation env loaded — ROS_DOMAIN_ID=$ROS_DOMAIN_ID, RMW=$RMW_IMPLEMENTATION"
