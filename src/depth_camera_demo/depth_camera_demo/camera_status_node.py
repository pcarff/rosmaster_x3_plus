import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import time

class CameraStatusNode(Node):
    def __init__(self):
        super().__init__('camera_status_node')
        self.color_received = 0
        self.depth_received = 0
        self.last_color_time = 0
        self.last_depth_time = 0

        # Subscriptions
        self.color_sub = self.create_subscription(Image, '/camera/color/image_raw', self.color_callback, 10)
        self.depth_sub = self.create_subscription(Image, '/camera/depth/image_raw', self.depth_callback, 10)

        # Status publisher
        self.status_pub = self.create_publisher(String, '/camera/status', 10)

        # Timer to publish status every 2 seconds
        self.timer = self.create_timer(2.0, self.timer_callback)
        self.get_logger().info('Camera Status Node Started!')

    def color_callback(self, msg):
        self.color_received += 1
        self.last_color_time = time.time()

    def depth_callback(self, msg):
        self.depth_received += 1
        self.last_depth_time = time.time()

    def timer_callback(self):
        current_time = time.time()
        color_status = "OK" if (current_time - self.last_color_time < 2.0) else "TIMEOUT"
        depth_status = "OK" if (current_time - self.last_depth_time < 2.0) else "TIMEOUT"

        status_msg = String()
        status_msg.data = f"Color: {color_status} ({self.color_received} frames) | Depth: {depth_status} ({self.depth_received} frames)"
        self.status_pub.publish(status_msg)
        self.get_logger().info(f'Published Status: {status_msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = CameraStatusNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
