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

### Stream Control (The "Toggles")
- **`enable_color` / `enable_depth` / `enable_ir`** (Default: `true`)
    - **Effect:** Setting these to `false` stops the camera from sending that data over USB.
    - **Use Case:** Turn off `enable_color` to save Jetson CPU if you only need 3D obstacle avoidance.

### Resolution and Framerate (The "Detail")
- **`color_width` / `color_height` / `color_fps`**
- **`depth_width` / `depth_height` / `depth_fps`**
    - **Effect:** Higher resolutions (e.g., 640x480) give better detail but use more USB bandwidth.
    - **Effect:** Higher FPS (e.g., 30) gives smoother motion, while lower FPS (e.g., 10) can make the point cloud more stable and "thicker" as the CPU has more time to process.

### Depth Registration (The "Alignment")
- **`depth_registration`** (Default: `true`)
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

## 5. Visualizing with RViz2

### Steps to see the Point Cloud:
1. **Fixed Frame:** Ensure this is set to **`camera_link`**.
2. **Add PointCloud2:** 
   - Click `Add` -> `By topic` tab.
   - Select `/camera/depth/color/points` -> `PointCloud2`.
3. **Optimize View:**
   - **Size (m):** Change from `0.01` to `0.03` to make points easier to see.
   - **Color Transformer:** Set to `RGB8` to see real-world colors.
   - **Style:** Set to `Points`.

---

## 6. Health Monitoring (Sensing Heartbeat)

We have created a custom node to monitor the health of the camera streams. It provides a simple text status of whether frames are arriving.

**Run on the robot:**
```bash
ros2 run depth_camera_demo camera_status_node
```

**Topic to watch (on Workstation/Foxglove):**
- `/camera/status` -> Reports: `Color: OK (### frames) | Depth: OK (### frames)`

---

## 7. Sample Code Demo

Want to write code that reacts to the depth camera? Imagine an app that calculates the distance to the exact center of the screen (e.g., measuring how far away an object is). 

You do this by subscribing to the `/camera/depth/image_raw` topic. The ROS `sensor_msgs/msg/Image` for depth contains an array of numbers (usually 16-bit integers) representing distance in millimeters.

**Example script location:** `src/depth_camera_demo/depth_camera_demo/center_distance_node.py`

```python
# Key conversion snippet:
depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
distance_mm = depth_image[height // 2, width // 2]
distance_m = distance_mm / 1000.0
```
