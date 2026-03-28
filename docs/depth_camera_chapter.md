# Chapter 2: The Orbbec Astra Pro (Depth Camera)

## 1. What is an RGB-D Camera?
The **Orbbec Astra Pro** is an **RGB-D** camera. This means it captures standard color video (RGB) and also measures the distance to every pixel in the image (Depth). 

Unlike the 2D LiDAR (which spins a laser full circle but only in a flat plane), the Astra Pro projects an invisible grid of infrared light straight ahead. By reading how that grid distorts over physical objects, it instantly calculates a highly detailed **3D Point Cloud** of everything in front of it.

**Why use both?**
- **LiDAR** is best for wide-area navigation, 360° obstacle avoidance, and mapping room layouts up to 50 meters away.
- **Depth Cameras** excel at close-range (up to ~8m), detailed 3D sensing. You use it to recognize objects, let the robotic arm pick up specifically shaped items, and avoid small obstacles (like table legs or shoes) that might fall under or above the flat laser beam.

---

## 2. Hardware Identifiers

The Astra Pro Plus presents itself as **two** separate USB devices:

| USB ID | Name | Purpose |
|---|---|---|
| `2bc5:050f` | USB 2.0 Camera | Color (RGB) sensor via UVC |
| `2bc5:060f` | ORBBEC Depth Sensor | Depth + IR sensor via OpenNI2 |

- **Serial Number**: `ACRK9430012`
- **Video Devices**: `/dev/video0`, `/dev/video1`
- **udev Rules**: Installed at `/etc/udev/rules.d/` (Orbbec-specific, granting `video` group access)

### Verifying Detection

Use the built-in list tool to confirm OpenNI2 can see the depth sensor:

```bash
ros2 launch astra_camera list_devices.launch.xml
```

Expected output:
```
Found 1 devices
Device connected: Astra
URI: 2bc5/060f@1/12
Serial number: ACRK9430012
```

---

## 3. Key Capabilities & ROS2 Parameters

The camera uses the `astra_camera` ROS2 package. When launching it, you have access to a massive list of parameters to control its performance.

### Stream Control (The "Toggles")
- **`enable_color` / `enable_depth` / `enable_ir`** (Default: `true`)
    - **Effect:** Setting these to `false` stops the camera from sending that data over USB.
    - **Use Case:** Turn off `enable_color` to save Jetson CPU if you only need 3D obstacle avoidance.

### Resolution and Framerate (The "Detail")
- **`color_width` / `color_height` / `color_fps`**
- **`depth_width` / `depth_height` / `depth_fps`**
    - **Effect:** Higher resolutions (e.g., 640x480) give better detail but use more USB bandwidth.
    - **Effect:** Higher FPS (e.g., 30) gives smoother motion, while lower FPS (e.g., 10) can make the point cloud more stable and "thicker" as the CPU has more time to process.

> **⚠️ CRITICAL: Supported Color (UVC) Modes**
>
> The color sensor only supports **specific resolution/FPS combinations**. Using an unsupported combination will crash the driver with `set uvc ctrl error Invalid mode` (SIGSEGV).

#### MJPEG Format (Default — Recommended)

| Resolution | FPS |
|---|---|
| 1920×1080 | 30 |
| 2048×1536 | 30 |
| 1280×960 | 30 |
| 1280×720 | 30 |
| **640×480** | **30** |
| 320×240 | 30 |

> MJPEG only supports **30 fps** at every resolution. Do **not** request 10 or 15 fps — it will crash.

#### YUYV Format (Uncompressed — Higher Bandwidth)

| Resolution | FPS |
|---|---|
| 1920×1080 | 3 |
| 2048×1536 | 3 |
| 1280×960 | 10 |
| 1280×720 | 10 |
| 640×480 | 30 |
| 320×240 | 30 |

#### Depth Sensor Modes

The depth stream supports `640x480@30Hz` with `PIXEL_FORMAT_DEPTH_1_MM`. The requested fps (e.g., 15) may be silently overridden to 30 by the driver.

### Depth Registration (The "Alignment")
- **`depth_registration`** (Default: `false` in launch file, set to `true`)
    - **Effect:** Because the RGB and Depth lenses are physically separated, their images are slightly offset. Setting this to `true` uses hardware math to "warp" the depth image to perfectly match the color feed.
    - **Use Case:** **Must be `true`** if you want a **Colored** Point Cloud where every 3D point has the correct RGB color.

### Point Cloud Generation (The "3D View")
- **`enable_point_cloud`** (Default: `true`)
    - **Effect:** Generates a 3D XYZ cloud without color.
- **`enable_colored_point_cloud`** (Default: `false`)
    - **Effect:** Attaches the exact RGB color to every 3D point. This is very "heavy" on the network/DDS and may lag over slow WiFi.

### UVC Parameters (The "Video Driver")
- **`uvc_product_id`** (Set to: `0x050f` for this robot)
    - **Effect:** Tells the driver which USB device is the color sensor.
- **`uvc_camera_format`** (Default: `mjpeg`)
    - **Effect:** Uses compressed MJPEG to save USB bandwidth.

---

## 4. How to Launch the Camera

> **Launch file**: `astro_pro_plus.launch.xml` (note the typo in the filename — "astro" not "astra")

### Step 1: Matching the Middleware (RMW)
Both the robot and your workstation must use the same ROS2 middleware. We use **CycloneDDS** for the best stability over WiFi.

**On the Robot:**
```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=42
```

**On your Workstation:**
Ensure your `setup_env.bash` includes:
```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=42
```

### Step 2: Launch Command

The recommended default launch (640×480 @ 30fps with colored point cloud):

```bash
ros2 launch astra_camera astro_pro_plus.launch.xml \
  depth_registration:=true \
  enable_colored_point_cloud:=true \
  publish_tf:=true \
  depth_width:=640 depth_height:=480 \
  color_width:=640 color_height:=480 \
  depth_fps:=30 color_fps:=30
```

Or use the convenience script on the robot:

```bash
~/launch_camera.sh
```

### Published Topics

| Topic | Type | Description |
|---|---|---|
| `/camera/color/image_raw` | `sensor_msgs/Image` | RGB video feed |
| `/camera/depth/image_raw` | `sensor_msgs/Image` | Depth image (16-bit, mm) |
| `/camera/depth/points` | `sensor_msgs/PointCloud2` | XYZ point cloud (no color) |
| `/camera/depth_registered/points` | `sensor_msgs/PointCloud2` | Colored point cloud (remapped from `/camera/depth/color/points`) |
| `/camera/ir/image_raw` | `sensor_msgs/Image` | Infrared image |
| `/camera/color/camera_info` | `sensor_msgs/CameraInfo` | Color camera intrinsics |
| `/camera/depth/camera_info` | `sensor_msgs/CameraInfo` | Depth camera intrinsics |
| `/tf` | `tf2_msgs/TFMessage` | Camera transform frames (at 10 Hz) |

---

## 5. Troubleshooting

### "Found 0 devices"
- Verify the camera appears in `lsusb` (look for `2bc5:050f` and `2bc5:060f`).
- Ensure udev rules are installed: `ls /etc/udev/rules.d/*orbbec*`.
- Run `ros2 launch astra_camera list_devices.launch.xml` to test OpenNI2 detection.
- If the camera was previously working, a USB reset may be needed (see below).

### "set uvc ctrl error Invalid mode" (Crash / SIGSEGV)
This means you requested an unsupported resolution/FPS combination for the UVC color sensor. **MJPEG only supports 30 fps.** See the supported modes table in Section 3.

### Camera Crash Kills `/dev/video*`
If the driver crashes (e.g., from an invalid mode), the USB device handles may disappear. To recover **without physically unplugging**:

```bash
# Reset USB ports to re-enumerate the camera
for port in /sys/bus/usb/drivers/usb/1-*; do
  p=$(basename "$port")
  [ -d "$port" ] && echo "$p" | sudo tee /sys/bus/usb/drivers/usb/unbind
  sleep 1
  [ -d "$port" ] || echo "$p" | sudo tee /sys/bus/usb/drivers/usb/bind
done
# Wait for re-enumeration
sleep 3
# Verify
lsusb | grep -i orbbec
ls -la /dev/video*
```

### Network Discovery (DDS)
If you can see topics in `ros2 topic list` but can't see images in RViz, your WiFi router is likely blocking **Multicast** traffic or the data fragments are too large.

**Bypassing with a Peer List:**
On your workstation, set the `CYCLONEDDS_URI` to point directly to the robot's IP:

```bash
export CYCLONEDDS_URI="<CycloneDDS><Domain><Discovery><Peers><Peer address='192.168.8.246'/></Peers></Discovery></Domain></CycloneDDS>"
```

---

## 6. Visualizing with RViz2

### Steps to see the Point Cloud:
1. **Fixed Frame:** Ensure this is set to **`camera_link`**.
2. **Add PointCloud2:** 
   - Click `Add` -> `By topic` tab.
   - Select `/camera/depth_registered/points` -> `PointCloud2`.
3. **Optimize View:**
   - **Reliability Policy:** Switch to **`Best Effort`** (Crucial for large data).
   - **Size (m):** Change from `0.01` to `0.03` to make points easier to see.

---

## 7. Visualizing with Foxglove

The robot has `ros-humble-foxglove-bridge` installed, which provides a high-performance native WebSocket connection.

### Starting the Bridge
On the robot (or via SSH):

```bash
source /opt/ros/humble/setup.bash
source ~/workspaces/x3plus_ws/install/setup.bash
export ROS_DOMAIN_ID=42
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 launch foxglove_bridge foxglove_bridge_launch.xml port:=8765
```

### Connecting Foxglove
1. Open Foxglove Studio.
2. Choose **"Open connection"** → **Foxglove WebSocket**.
3. Enter: **`ws://192.168.8.246:8765`**

### Recommended Panels
| Panel | Topic | Use |
|---|---|---|
| Image | `/camera/color/image_raw` | Live RGB feed |
| Image | `/camera/depth/image_raw` | Depth visualization |
| 3D | `/camera/depth_registered/points` | Colored point cloud |

---

## 8. Creating a Digital Twin

A Digital Twin combines the 3D Point Cloud with a virtual model of the robot (URDF).

### In Foxglove:
1. **Add a 3D Panel.**
2. **Paste URDF:** Under Settings -> Robot Model -> URDF, paste the robot's description XML.
3. **Set Mesh Source:** Set to "Robot Description" to load the 3D meshes.
4. **Subscribe to Points:** Check the `/camera/depth_registered/points` topic. 

The live point cloud will now be perfectly aligned with the virtual robot's camera mount.

---

## 9. Sample Code Demo

Want to write code that reacts to the depth camera? Imagine an app that calculates the distance to the exact center of the screen (e.g., measuring how far away an object is). 

You do this by subscribing to the `/camera/depth/image_raw` topic. The ROS `sensor_msgs/msg/Image` for depth contains an array of numbers (usually 16-bit integers) representing distance in millimeters.

**Example script location:** `src/depth_camera_demo/depth_camera_demo/center_distance_node.py`

```python
# Key conversion snippet:
depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
distance_mm = depth_image[height // 2, width // 2]
distance_m = distance_mm / 1000.0
```
