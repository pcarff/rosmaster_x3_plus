# Chapter 3: Mecanum Wheels & Teleoperation

## 1. The Magic of Mecanum Wheels

Your Rosmaster X3 Plus is equipped with four **Mecanum wheels**. Unlike standard rubber tires that only roll forward and backward, Mecanum wheels have small angled rollers around their circumference (usually at a 45-degree angle). 

By driving the four wheels in specific combinations of forward and backward directions, the robot can achieve **omnidirectional movement**:
- **Forward/Backward:** All four wheels spin the same direction.
- **Rotate:** Left wheels spin backward, Right wheels spin forward.
- **Strafe (Move sideways):** Front-left and back-right spin forward; Front-right and back-left spin backward. The opposing forces cancel out forward motion and push the robot perfectly sideways!

### The Motor Driver (Rosmaster_Lib)
Normally, calculating the math to spin the four motors at different speeds to achieve a perfect 45-degree strafe is complicated. Yaboom provides a Python library called `Rosmaster_Lib` which handles this MCU-level kinematics math for us!

Instead of sending PWM signals to each motor, we can simply say:
```python
# robot.set_car_motion(velocity_x, velocity_y, angular_z)
robot.set_car_motion(0.0, 0.5, 0.0) # Strafe left at 0.5 m/s
```

---

## 2. ROS2 Teleoperation with `/cmd_vel`

In the ROS2 ecosystem, robots don't usually accept raw motor PWM signals from planners. Instead, they expect a standard message on a topic called `/cmd_vel` (Command Velocity). 

The message type is `geometry_msgs/msg/Twist`, which contains two parts:
- `linear` (x, y, z): Movement in meters per second.
- `angular` (x, y, z): Rotation in radians per second.

For a ground robot:
- `linear.x` moves you Forward/Backward.
- `linear.y` moves you Left/Right (Strafing, only possible with Mecanum/Omni wheels).
- `angular.z` rotates you in place.

### The Custom `rosmaster_base` Node
Since your robot's original Yaboom workspace was erased, we built a brand new, lightweight ROS2 driver from scratch! You can find it in your workspace at `src/rosmaster_base`. 

Its job is simple:
1. Listen to the `/cmd_vel` topic.
2. Read the `Twist` message.
3. Pass the `x`, `y`, and `z` values directly into the `Rosmaster_Lib` hardware controller.
4. Stop the robot if no messages are received for 0.5 seconds (a safety "Watchdog" timer).

---

## 3. How to Drive the Robot

Because ROS2 is distributed (using Cyclone DDS), you can run the base controller on the robot and the keyboard controller on your powerful workstation.

**Step 1: Start the Base Controller on the Robot**
Open a terminal and SSH into the robot to launch the hardware bridge:
```bash
ssh x3
source ~/workspaces/anzym_ros_ws/install/setup.bash
export ROS_DOMAIN_ID=42
ros2 run rosmaster_base base_controller
```
*(You should see "Connected to Rosmaster X3 Plus hardware successfully!")*

**Step 2: Start the Keyboard Teleop on your Workstation**
Open a new terminal on your Ubuntu workstation:
```bash
source ~/Workspaces/x3_plus/setup_env.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**How to Drive:**
- `i` : Move forward
- `,` : Move backward
- `j` : Rotate left
- `l` : Rotate right
- **`u` / `o` / `m` / `.`** : Strafe in 45-degree diagonals!

Try driving it around! Notice how fast the robot responds because your workstation and the Jetson are sharing information instantly over the network via DDS.
