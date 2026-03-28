# Chapter 2: The Orbbec Astra Pro (Depth Camera)

## 1. What is an RGB-D Camera?
The **Orbbec Astra Pro** is an **RGB-D** camera. This means it captures standard color video (RGB) and also measures the distance to every pixel in the image (Depth). 

Unlike the 2D LiDAR (which spins a laser full circle but only in a flat plane), the Astra Pro projects an invisible grid of infrared light straight ahead. By reading how that grid distorts over physical objects, it instantly calculates a highly detailed **3D Point Cloud** of everything in front of it.

**Why use both?**
- **LiDAR** is best for wide-area navigation, 360° obstacle avoidance, and mapping room layouts up to 50 meters away.
- **Depth Cameras** excel at close-range (up to ~8m), detailed 3D sensing. You use it to recognize objects, let the robotic arm pick up specifically shaped items, and avoid small obstacles (like table legs or shoes) that might fall under or above the flat laser beam.

---

## 2. Key Capabilities & ROS2 Parameters

The camera uses the `astra_camera` ROS2 package. When launching it, you have access to a massive list of parameters to control its performance.

### Resolution and Framerate
By default, the camera runs at **640x480 at 30 FPS**. You can change these using:
- `color_width` / `color_height` / `color_fps`
- `depth_width` / `depth_height` / `depth_fps`
- `ir_width` / `ir_height` / `ir_fps` (Infrared image stream)

> *Tip: Higher resolutions give better detail but use significantly more USB bandwidth and Jetson CPU power to process.*

### Point Cloud Generation
The node can mathematically combine the 2D depth image and the 2D color image into a true 3D space:
- **`enable_point_cloud`** (default: `true`): Generates a 3D XYZ cloud without color.
- **`enable_colored_point_cloud`** (default: `false`): Attaches the exact RGB color to every 3D point. This looks amazing in RViz but takes more processing overhead.
- **`depth_registration`** (default: `true`): **Crucial parameter.** Because the depth sensor and the color lens are physically sitting next to each other on the camera bar, their perspectives are slightly misaligned. Setting this to `true` uses a hardware feature to warp the depth map to perfectly align with the color image, fixing "color bleeding" on the edges of objects in the 3D cloud.

### Toggling Streams
To save USB bandwidth, turn off streams you don't need:
- `enable_color`, `enable_depth`, `enable_ir` (defaults: `true`)

---

## 3. How to Launch the Camera

To ensure the camera works reliably across the network (RViz and Foxglove), follow these exact steps.

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

### Step 2: Executing the Launcher
On this robot, the color sensor uses a specific product ID (`0x050f`). We also enable TF publishing so RViz can see the 3D data.

```bash
source /opt/ros/humble/setup.bash
source ~/workspaces/x3plus_ws/install/setup.bash
ros2 launch astra_camera astra_pro.launch.xml uvc_product_id:=0x050f publish_tf:=true
```

---

## 4. Troubleshooting Network Discovery (DDS)

If you can see topics in `ros2 topic list` but can't see images in RViz, your WiFi router is likely blocking **Multicast** traffic. You can fix this by telling ROS2 exactly where the other machine is (Unicast).

### Bypassing with a Peer List
On your workstation, set the `CYCLONEDDS_URI` to point directly to the robot's IP:

```bash
export CYCLONEDDS_URI="<CycloneDDS><Domain><Discovery><Peers><Peer address='192.168.8.246'/></Peers></Discovery></Domain></CycloneDDS>"
```

---

## 5. Health Monitoring (Sensing Heartbeat)

We have created a custom node to monitor the health of the camera streams. It provides a simple text status of whether frames are arriving.

**Run on the robot:**
```bash
ros2 run depth_camera_demo camera_status_node
```

**Topic to watch (on Workstation/Foxglove):**
- `/camera/status` -> Reports: `Color: OK (### frames) | Depth: OK (### frames)`

---

## 6. Sample Code Demo

Want to write code that reacts to the depth camera? Imagine an app that calculates the distance to the exact center of the screen (e.g., measuring how far away an object is). 

You do this by subscribing to the `/camera/depth/image_raw` topic. The ROS `sensor_msgs/msg/Image` for depth contains an array of numbers (usually 16-bit integers) representing distance in millimeters.

**Example script location:** `src/depth_camera_demo/depth_camera_demo/center_distance_node.py`

```python
# Key conversion snippet:
depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
distance_mm = depth_image[height // 2, width // 2]
distance_m = distance_mm / 1000.0
```
