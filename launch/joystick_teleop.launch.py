import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Start the Joy Node to read /dev/input/js0
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen',
            parameters=[{
                'dev': '/dev/input/js0',
                'deadzone': 0.1,
                'autorepeat_rate': 20.0,
            }]
        ),
        
        # 2. Start the Teleop Node to convert Joy -> Twist messages
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy_node',
            output='screen',
            parameters=[{
                # Standard button layout mapping (Requires holding enable button to move)
                # Button 0 is usually 'A' or 'Cross'. Button 5 is usually 'R1' / 'Right Bumper'
                'require_enable_button': True,
                'enable_button': 0, # Or 5
                
                # Axis 1 = Left Stick Vertical. Scale to max 0.5 m/s
                'axis_linear.x': 1,
                'scale_linear.x': 0.7,
                
                # Axis 0 = Left Stick Horizontal. Used for STRFAING (Y-axis linear velocity)
                'axis_linear.y': 0,
                'scale_linear.y': 0.7,
                
                # Axis 3 or 4 = Right Stick Horizontal. Used for Rotation (Z-axis angular velocity)
                # Some controllers map Right stick X to 3, Xbox maps it to 3 or 4.
                'axis_angular.yaw': 3,
                'scale_angular.yaw': 1.5,
            }]
        )
    ])
