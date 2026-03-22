# Rosmaster X3 Plus — Session Log

> Running journal of everything we do with the robot, in chronological order.

---

## 2026-03-22 — Session 1: Environment Setup

### 11:46 — Project Kickoff
- Decided on a component-by-component learning path toward full autonomy
- Created the `~/Workspaces/x3_plus` workspace as our development home base
- Researched the X3 Plus specs and component list

### 11:51 — SSH Key Authentication
- Robot is at `jetson@192.168.8.246` on the `192.168.8.x` LAN
- Copied existing `~/.ssh/id_ed25519` key to the robot via `ssh-copy-id`
- Created SSH config alias: **`ssh x3`** connects instantly without password
- **Config file**: `~/.ssh/config`

### 11:56 — Robot Reconnaissance
Discovered current state of the robot:

| Detail | Value |
|---|---|
| Hostname | `yahboom` |
| JetPack | R36.4.7 |
| Kernel | 5.15.148-tegra (aarch64) |
| RAM | 16 GB |
| Disk | 147 GB (90% full — only 16 GB free) |

**Connected USB devices**: Orbbec depth camera, 2x CH340 serial (motors/arm), CP210x UART (LiDAR), Bluetooth, LED display

**ROS2 packages pre-installed**: Nav2 full stack, slam_toolbox, rtabmap_slam, teleop_twist_keyboard, teleop_twist_joy, joy, imu_filter_madgwick

### 12:17 — Multi-Machine Development Workflow
- Chose the **develop-on-workstation, deploy-to-robot** model
- Installed **Cyclone DDS** (`rmw_cyclonedds_cpp`) on both machines for reliable multi-machine communication
- Set **`ROS_DOMAIN_ID=42`** on both machines so they share topic discovery
- Created `cyclonedds.xml` with multicast + explicit unicast peers
- Configured robot's `~/.bashrc` with ROS env vars
- **Verified cross-machine communication**: robot published a topic, workstation received it ✅

**Files created**:
- `setup_env.bash` — source on workstation to load all ROS2 env vars
- `scripts/deploy.sh` — rsync packages to robot + remote colcon build
- `cyclonedds.xml` — DDS discovery config (copied to both machines)

### 12:39 — LiDAR Exploration
- Discovered pre-built `ydlidar_ros2_driver` in `~/workspaces/anzym_ros_ws/` on robot
- LiDAR model: **YDLIDAR TG30** (TOF), serial: 2025011300100037, firmware: 2.1
- Fixed Cyclone DDS config incompatibility (removed `<Interfaces>` element unsupported on robot)
- Fixed Domain ID issue — first launch used Domain 0 instead of 42
- Created `~/launch_lidar.sh` on robot for reliable launches with correct env vars
- Verified `/scan` topic at **10 Hz** on workstation (`sensor_msgs/msg/LaserScan`, ~2020 points/scan)
- Also found `/point_cloud` topic (`PointCloud2`)
- Created `rviz/lidar_view.rviz` config and launched RViz2 for visualization

### 15:22 — Documentation: LiDAR Chapter
- Created a new reference document: `docs/lidar_chapter.md`
- Outlined basic LiDAR concepts and ToF
- Documented YDLIDAR TG30 parameters (frequency, sample rate, angle bounds, etc.)
- Described conceptual approaches for using 2D LiDAR to build a 3D scanner app (Pan-tilt sweeping, driving SLAM/Octomap, and using the existing depth camera instead).

### 15:31 — Documentation: Depth Camera Chapter
- Created a new reference document: `docs/depth_camera_chapter.md`
- Outlined RGB-D capabilities of the Orbbec Astra Pro
- Configured params: `depth_registration`, `enable_colored_point_cloud`
- Created `~/launch_camera.sh` script on the robot
- Visualized `/camera/depth/color/points` and `/camera/color/image_raw`
- Added RViz2 instructions to both LiDAR and Depth Camera chapters
- Created RViz2 visualization config: `rviz/camera_view.rviz`
- Created a sample ROS2 Python node (`depth_camera_demo`) to print the distance at the center of the camera feed.

---

*— End of Session 1 —*
