"""Spawn a static, unmapped box into the running Gazebo world."""
import subprocess

import rclpy
from rclpy.node import Node

BOX_SDF = (
    '<sdf version="1.9"><model name="{name}"><static>true</static>'
    '<link name="link"><collision name="c"><geometry><box><size>0.3 0.3 0.5</size>'
    '</box></geometry></collision><visual name="v"><geometry><box>'
    '<size>0.3 0.3 0.5</size></box></geometry></visual></link></model></sdf>'
)


def spawn_box(name='demo_box', x=-0.55, y=-0.55):
    """Spawn the box with ros_gz_sim create (z=0.25 puts it on the floor)."""
    cmd = ['ros2', 'run', 'ros_gz_sim', 'create', '-name', name,
           '-x', str(x), '-y', str(y), '-z', '0.25',
           '-string', BOX_SDF.format(name=name)]
    return subprocess.run(cmd, capture_output=True).returncode == 0


def main():
    rclpy.init()
    node = Node('spawn_obstacle')
    name = node.declare_parameter('name', 'demo_box').value
    x = node.declare_parameter('x', -0.55).value
    y = node.declare_parameter('y', -0.55).value
    ok = spawn_box(name, x, y)
    print(f'Obstacle "{name}" at ({x}, {y}): {"spawned" if ok else "FAILED"}')
    rclpy.shutdown()


if __name__ == '__main__':
    main()
