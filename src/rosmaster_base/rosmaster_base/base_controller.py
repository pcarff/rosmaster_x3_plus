import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

try:
    from Rosmaster_Lib import Rosmaster
    HAS_ROSMASTER = True
except ImportError:
    HAS_ROSMASTER = False

class BaseController(Node):
    def __init__(self):
        super().__init__('base_controller')
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10)
        
        if HAS_ROSMASTER:
            self.robot = Rosmaster()
            self.robot.create_receive_threading()  # Ensure serial reading thread is active
            self.get_logger().info('Connected to Rosmaster X3 Plus hardware successfully!')
        else:
            self.get_logger().warn('Rosmaster_Lib not found. Running in simulation/mock mode.')
            self.robot = None

        # Watchdog logic: Stop robot if communication drops
        self.last_cmd_time = time.time()
        self.timer = self.create_timer(0.5, self.watchdog_timer)
        self.get_logger().info('Base controller node started. Listening to /cmd_vel...')

    def cmd_vel_callback(self, msg):
        self.last_cmd_time = time.time()
        
        # Mecanum Wheel Kinematics mapping:
        # linear.x: Forward/Backward (m/s)
        # linear.y: Strafe Left/Right (m/s)  <-- Mecanum magic
        # angular.z: Rotate Left/Right (rad/s)
        
        if self.robot:
            self.robot.set_car_motion(msg.linear.x, msg.linear.y, msg.angular.z)
        else:
            self.get_logger().info(f'Mock drive: V_x={msg.linear.x:.2f}, V_y={msg.linear.y:.2f}, V_z={msg.angular.z:.2f}')

    def watchdog_timer(self):
        # Stop the robot if we haven't received a command in 0.5 seconds
        if time.time() - self.last_cmd_time > 0.5:
            if self.robot:
                self.robot.set_car_motion(0.0, 0.0, 0.0)

def main(args=None):
    rclpy.init(args=args)
    base_controller = BaseController()
    try:
        rclpy.spin(base_controller)
    except KeyboardInterrupt:
        pass
    finally:
        if base_controller.robot:
            base_controller.robot.set_car_motion(0.0, 0.0, 0.0)
            del base_controller.robot
        base_controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
