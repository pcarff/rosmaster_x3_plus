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
- **`depth_registration`** (default: `false`): **Crucial parameter.** Because the depth sensor and the color lens are physically sitting next to each other on the camera bar, their perspectives are slightly misaligned. Setting this to `true` uses a hardware feature to warp the depth map to perfectly align with the color image, fixing "color bleeding" on the edges of objects in the 3D cloud.

### Toggling Streams
To save USB bandwidth, turn off streams you don't need:
- `enable_color`, `enable_depth`, `enable_ir` (defaults: `true`)

---

## 3. How to Launch the Camera

We have created a helper script on the robot that automatically sets the correct `ROS_DOMAIN_ID` and turns on hardware depth registration and colored point clouds for the best 3D visualization.

1. **SSH to the robot:**
   ```bash
   ssh x3
   ```
2. **Execute the launcher:**
   ```bash
   bash ~/launch_camera.sh
   ```

### What Topics are Published?
Once running, you'll see a wealth of topics when you type `ros2 topic list` on your workstation. The most important ones are under the `/camera/` namespace:
- `/camera/color/image_raw` — Standard 2D video feed
- `/camera/depth/image_raw` — Raw 2D depth map (visualized as grayscale)
- `/camera/depth/color/points` — The fully assembled 3D Colored Point Cloud

---

## 4. Visualizing with RViz2

Seeing a colored point cloud is one of the most satisfying parts of robotics. We have prepared an RViz2 configuration specifically for the camera.

1. **On your workstation**, after launching the camera on the robot:
   ```bash
   source ~/Workspaces/x3_plus/setup_env.bash
   rviz2 -d ~/Workspaces/x3_plus/rviz/camera_view.rviz
   ```
2. **Inside RViz:**
   - **Fixed Frame:** Ensure this is set to `camera_link`.
   - **Displays Panel:**
     - Enable the `Image` display to see the live 2D `/camera/color/image_raw` feed.
     - Enable the `PointCloud2` display to see the 3D projection from `/camera/depth/color/points`.
   - **Interaction:** Use your mouse to click and drag in the main window. You can fly around the 3D points and see the true depth of the room!

---

## 5. Sample Code Demo

Want to write code that reacts to the depth camera? Imagine an app that calculates the distance to the exact center of the screen (e.g., measuring how far away an object is). 

You do this by subscribing to the `/camera/depth/image_raw` topic. The ROS `sensor_msgs/msg/Image` for depth contains an array of numbers (usually 16-bit integers) representing distance in millimeters.

*(For a full working example of this script, create a ROS2 Python package in your workspace and subscribe to `sensor_msgs.msg.Image` on `/camera/depth/image_raw`.)*
