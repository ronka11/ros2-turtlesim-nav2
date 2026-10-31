from glob import glob

from setuptools import find_packages, setup

package_name = 'tb3_nav2_demo'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ronka',
    maintainer_email='raunak.rajput6600@gmail.com',
    description='TurtleBot3 autonomous navigation demo with Nav2 on ROS 2 Jazzy and Gazebo Harmonic',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'send_goal = tb3_nav2_demo.send_goal:main',
            'spawn_obstacle = tb3_nav2_demo.spawn_obstacle:main',
            'demo_runner = tb3_nav2_demo.demo_runner:main',
        ],
    },
)
