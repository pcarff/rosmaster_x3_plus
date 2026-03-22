# Rosmaster X3 Plus — Reference Guide

> Detailed reference of every configuration step, what it does, and why.

---

## 1. SSH Key Authentication

**Goal**: Log into the robot without typing a password every time.

**How it works**: SSH key pairs use asymmetric cryptography. Your workstation holds a *private* key (`~/.ssh/id_ed25519`), and the robot holds the matching *public* key (`~/.ssh/authorized_keys`). When you connect, the robot challenges you with the public key, and your machine proves identity with the private key — no password needed.

**What we did**:
```bash
# Copy your public key to the robot's authorized_keys
ssh-copy-id -i ~/.ssh/id_ed25519.pub jetson@192.168.8.246
```

**SSH config alias** (`~/.ssh/config`):
```
Host x3
    HostName 192.168.8.246
    User jetson
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
```
Now `ssh x3` is all you need. This alias is also used by `scp`, `rsync`, and the deploy script.

---

## 2. ROS2 Multi-Machine Architecture

**Goal**: Develop on your powerful workstation, run hardware nodes on the robot, and have both see each other's ROS2 topics seamlessly.

**Why this approach**:
- The Jetson's disk is nearly full (90%) — not ideal for IDEs and dev tools
- ARM compilation is slow compared to your x86 workstation
- Visualization tools (RViz2, Gazebo) need a display and GPU
- ROS2's DDS middleware natively supports multi-machine communication

**Architecture**:
```
  WORKSTATION (192.168.8.173)              ROBOT (192.168.8.246)
  ┌──────────────────────────┐             ┌──────────────────────┐
  │ Code editing / IDE       │  Cyclone    │ Motor drivers        │
  │ RViz2 visualization      │◄───DDS────► │ LiDAR node           │
  │ Gazebo simulation        │  Domain 42  │ Camera node          │
  │ Nav2 planning (optional) │             │ IMU / Arm nodes      │
  └──────────────────────────┘             └──────────────────────┘
```

---

## 3. ROS_DOMAIN_ID

**What**: An integer (0–232) that partitions ROS2 traffic. Only nodes with the **same Domain ID** can discover each other.

**Why we use 42**: The default (0) means every ROS2 program on the network talks to each other — including other people's robots or test scripts. Setting a non-zero value (`42`) isolates our traffic.

**Where it's set**:
- Workstation: `setup_env.bash` → `export ROS_DOMAIN_ID=42`
- Robot: `~/.bashrc` → `export ROS_DOMAIN_ID=42`

---

## 4. Cyclone DDS (RMW Layer)

**What**: ROS2 doesn't do networking itself — it delegates to a **DDS middleware**. The default is FastRTPS, but **Cyclone DDS** is more reliable for multi-machine setups.

**Why we switched**: FastRTPS can be finicky with topic discovery across machines, especially with mixed network interfaces (WiFi + Docker bridges). Cyclone DDS has better multicast handling and explicit peer configuration.

**What we installed**:
```bash
# On both machines:
sudo apt-get install ros-humble-rmw-cyclonedds-cpp
```

**Environment variable** (both machines):
```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

### Cyclone DDS Config (`cyclonedds.xml`)

Located at:
- Workstation: `~/Workspaces/x3_plus/cyclonedds.xml`
- Robot: `~/cyclonedds.xml`

```xml
<CycloneDDS>
  <Domain>
    <General>
      <AllowMulticast>true</AllowMulticast>
    </General>
    <Interfaces>
      <NetworkInterface autodetermine="true" multicast="true"/>
    </Interfaces>
    <Discovery>
      <Peers>
        <Peer address="192.168.8.246"/>  <!-- Robot -->
        <Peer address="192.168.8.173"/>  <!-- Workstation -->
      </Peers>
    </Discovery>
  </Domain>
</CycloneDDS>
```

**Key config choices**:
- `AllowMulticast=true` — enables automatic discovery on the LAN
- `Peers` — explicit unicast fallback in case multicast doesn't work (common with some WiFi drivers)
- `autodetermine="true"` — lets Cyclone pick the right network interface

**Referenced by**: `export CYCLONEDDS_URI=file:///path/to/cyclonedds.xml`

---

## 5. Workspace Structure

```
~/Workspaces/x3_plus/          ← Colcon workspace root
├── setup_env.bash             ← Source this to load all env vars
├── cyclonedds.xml             ← DDS discovery config
├── scripts/
│   └── deploy.sh              ← Rsync + remote build
├── src/                       ← Your ROS2 packages go here
├── build/                     ← (created by colcon build)
├── install/                   ← (created by colcon build)
└── docs/
    ├── session_log.md         ← This running log
    └── reference_guide.md     ← This file
```

---

## 6. The Deploy Script (`scripts/deploy.sh`)

**What it does**:
1. Rsyncs your `src/` packages to the robot's `~/yahboomcar_ws/src/`
2. Runs `colcon build --symlink-install` on the robot remotely
3. Shows the last 20 lines of build output

**Usage**:
```bash
./scripts/deploy.sh              # Deploy ALL packages
./scripts/deploy.sh my_package   # Deploy one specific package
```

**Why `--symlink-install`**: Instead of copying Python files into `install/`, it symlinks them. This means you can edit Python scripts on the robot and changes take effect immediately without rebuilding.

**Rsync excludes**: `.git`, `build/`, `install/`, `log/`, `__pycache__`, `*.pyc` — these are local artifacts that shouldn't be transferred.

---

## 7. Daily Development Workflow

```bash
# 1. Source the environment (once per terminal)
source ~/Workspaces/x3_plus/setup_env.bash

# 2. Write/edit your ROS2 packages in src/

# 3. Deploy to robot
./scripts/deploy.sh

# 4. SSH to robot, run hardware nodes
ssh x3
source ~/yahboomcar_ws/install/setup.bash
ros2 launch <package> <launch_file>

# 5. On workstation, run visualization
rviz2                          # All robot topics appear automatically
ros2 topic list                # See what's publishing
ros2 topic echo /some_topic    # Inspect data
```

---

## Quick Reference

| What | Command |
|---|---|
| Connect to robot | `ssh x3` |
| Load workstation env | `source ~/Workspaces/x3_plus/setup_env.bash` |
| Deploy to robot | `./scripts/deploy.sh` |
| See all ROS2 topics | `ros2 topic list` |
| See all ROS2 nodes | `ros2 node list` |
| Inspect a topic | `ros2 topic echo /topic_name` |
| Launch RViz2 | `rviz2` |
| Check robot resources | `ssh x3 'free -h && df -h /'` |

---

## 8. YDLIDAR TG30 (LiDAR)

**What**: A 360° Time-of-Flight (TOF) laser range finder. It spins continuously and measures the distance to surrounding objects by timing how long a laser pulse takes to bounce back.

**Key specs**:
| Spec | Value |
|---|---|
| Model | TG30 |
| Scan Rate | 10 Hz (10 full rotations per second) |
| Sample Rate | 20,000 points/sec |
| Range | 0.01m – 50m |
| Connection | USB via CP210x UART → `/dev/ydlidar` |
| Baud Rate | 512,000 |
| ROS2 Topic | `/scan` (`sensor_msgs/msg/LaserScan`) |
| Also publishes | `/point_cloud` (`sensor_msgs/msg/PointCloud2`) |
| Frame ID | `laser_link` |

**How to launch**:
```bash
# On the robot:
ssh x3
bash ~/launch_lidar.sh
```

**How to visualize** (on workstation):
```bash
source ~/Workspaces/x3_plus/setup_env.bash
rviz2 -d ~/Workspaces/x3_plus/rviz/lidar_view.rviz
```

**What LaserScan contains**: Each message has:
- `ranges[]` — array of ~2020 distances (meters) for the full 360°
- `angle_min` / `angle_max` — the angular sweep (−180° to +180°)
- `angle_increment` — angle step between consecutive beams
- `time_increment` — time between consecutive beams
- `range_min` / `range_max` — valid measurement bounds

**Driver location**: Pre-built in `/home/jetson/workspaces/anzym_ros_ws/install/ydlidar_ros2_driver/`
**Config file**: `.../params/ydlidar.yaml`
**Launch helper**: `~/launch_lidar.sh` (sets Domain ID, Cyclone DDS, sources workspaces)

---

> **⚠️ Note**: If the robot's IP changes (e.g., DHCP lease renewal), update it in:
> 1. `~/.ssh/config` (Host x3)
> 2. `cyclonedds.xml` (Peer address) — on both machines
