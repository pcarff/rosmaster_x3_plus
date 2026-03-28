from setuptools import find_packages, setup

package_name = 'depth_camera_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pcarff',
    maintainer_email='pcarff@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'center_distance_node = depth_camera_demo.center_distance_node:main',
            'camera_status_node = depth_camera_demo.camera_status_node:main',
        ],
    },
)
