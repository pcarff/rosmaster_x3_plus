# Archive Code Reference

> Catalog of Yaboom-provided source code archives on this workstation.
> When code is copied into our workspace (`~/Workspaces/x3_plus`), it is documented below with attribution.

---

## Archive Location 1: `yahboomcar_ros2_ws`

**Path**: `/home/pcarff/Archive/For jetson orin super/yahboomcar_ros2_ws/`

### `yahboomcar_ws/src/` — 22 ROS2 Packages (Robot Application Code)

| Package | Purpose |
|---|---|
| `yahboomcar_base_node` | Base motor/hardware control node |
| `yahboomcar_bringup` | Launch and bringup files |
| `yahboomcar_ctrl` | Controller / teleop |
| `yahboomcar_astra` | Astra depth camera color tracking & HSV utilities |
| `yahboomcar_description` | URDF robot model (X3) |
| `yahboomcar_description_x1` | URDF robot model (X1 variant) |
| `yahboomcar_laser` | LiDAR processing |
| `yahboomcar_nav` | Navigation stack config |
| `yahboomcar_slam` | SLAM mapping config |
| `yahboomcar_linefollow` | Line following |
| `yahboomcar_KCFTracker` | KCF visual object tracking |
| `yahboomcar_mediapipe` | MediaPipe gesture control |
| `yahboomcar_visual` | Computer vision utilities |
| `yahboomcar_voice_ctrl` | Voice control |
| `yahboomcar_msgs` | Custom message definitions |
| `yahboomcar_rviz` | RViz configurations |
| `yahboomcar_point` | Point cloud processing |
| `yahboomcar_multi` | Multi-robot support |
| `laserscan_to_point_pulisher` | LaserScan → PointCloud converter |
| `robot_pose_publisher_ros2` | Robot pose publisher |
| `yahboom_app_save_map` | Map saving for app integration |
| `yahboom_web_savmap_interfaces` | Web map saving interfaces |

### `software/` — SDK and Library Sources

| Directory | Purpose |
|---|---|
| `OpenNI_ROS2_SDK_v1.1.0_20230131_d6d939/` | Orbbec OpenNI2 ROS2 camera driver source |
| `YDLidar-SDK/` | YDLIDAR SDK source |
| `dlib/` | dlib machine learning library |
| `g2o/` | Graph optimization framework (for SLAM) |
| `glog-0.6.0/` | Google logging library |
| `magic_enum-0.8.0/` | C++ enum utilities |
| `mediapipe_demo/` | MediaPipe demo code |
| `orbslam2/` | ORB-SLAM2 visual SLAM |
| `py_install_V0.0.1/` | Python install package (v0.0.1) |
| `py_install_V3.3.1/` | Python install package (v3.3.1) |

### `software/library_ws/` — Pre-built Library Workspace

Contains pre-compiled versions of key dependencies:

| Package | Purpose |
|---|---|
| `ros2_astra_camera` | **Orbbec Astra camera ROS2 driver** (C++, with bundled arm64 OpenNI2 binaries) |
| `ydlidar_ros2_driver` | YDLIDAR ROS2 driver |
| `ros2_gmapping` | GMapping SLAM |
| `sllidar_ros2` | SLAMTEC RPLidar driver |
| `costmap_converter-humble` | Costmap converter for navigation |
| `teb_local_planner-humble-devel` | TEB local planner |
| `robot_localization` | EKF/UKF robot localization |
| `web_video_server-ros2` | Web-based video streaming server |

---

## Archive Location 2: `yahboomcar_ros2_ws_yahboomcar_ws`

**Path**: `/home/pcarff/Archive/For jetson orin super/yahboomcar_ros2_ws_yahboomcar_ws/`

### `yahboomcar_ros2_ws/yahboomcar_ws/src/` — 8 ROS2 Tutorial Packages

| Package | Purpose |
|---|---|
| `pkg_helloworld_py` | Hello world example |
| `pkg_topic` | Topic pub/sub example |
| `pkg_service` | Service example |
| `pkg_param` | Parameter example |
| `pkg_action` | Action example |
| `pkg_tf` | TF2 transform example |
| `pkg_interfaces` | Custom interface definitions |
| `pkg_metapackage` | Metapackage |

---

## Code Copied Into Our Workspace

| Date | Source | Dest in `x3_plus/src/` | Reason |
|---|---|---|---|
| 2026-03-24 | Archive 1: `software/library_ws/src/ros2_astra_camera/` | `src/ros2_astra_camera/` | Orbbec Astra Pro depth camera ROS2 driver with bundled arm64 OpenNI2 libraries |
