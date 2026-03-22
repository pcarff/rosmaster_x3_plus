import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class CenterDistanceNode(Node):
    def __init__(self):
        super().__init__('center_distance_node')
        # Subscribe to the raw depth image topic
        self.subscription = self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_callback,
            10)
        self.bridge = CvBridge()
        self.get_logger().info('Depth center distance node started! Waiting for /camera/depth/image_raw...')

    def depth_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV image
            # Orbbec depth images are typically 16-bit encoding (16UC1) representing millimeters
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            
            # Get the dimensions of the image
            height, width = depth_image.shape
            
            # Find the center pixel
            center_x = width // 2
            center_y = height // 2
            
            # Get the depth value in millimeters at the center
            distance_mm = depth_image[center_y, center_x]
            
            # Convert to meters
            distance_m = distance_mm / 1000.0
            
            if distance_mm == 0:
                self.get_logger().info(f'Center point [{center_x}, {center_y}]: Out of range or blind spot')
            else:
                self.get_logger().info(f'Distance at center [{center_x}, {center_y}]: {distance_m:.3f} meters')
                
        except Exception as e:
            self.get_logger().error(f'Error processing depth image: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = CenterDistanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
