import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class CircleDriver(Node):
    def __init__(self):
        super().__init__('circle_driver')

        # Parameters with defaults (overridable from YAML, CLI, or launch)
        self.declare_parameter('linear_speed', 2.0)
        self.declare_parameter('angular_speed', 1.0)

        # Publisher: send velocity commands (same topic teleop used)
        self.cmd_pub = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)

        # Subscriber: receive the turtle's position
        self.create_subscription(Pose, 'turtle1/pose', self.on_pose, 10)

        # Timer: publish a command 10 times per second
        self.create_timer(0.1, self.on_timer)
        self.last_pose = None

    def on_pose(self, msg):
        self.last_pose = msg

    def on_timer(self):
        cmd = Twist()
        cmd.linear.x = self.get_parameter('linear_speed').value
        cmd.angular.z = self.get_parameter('angular_speed').value
        self.cmd_pub.publish(cmd)

        if self.last_pose is not None:
            self.get_logger().info(
                f'x={self.last_pose.x:.2f} y={self.last_pose.y:.2f} '
                f'theta={self.last_pose.theta:.2f}',
                throttle_duration_sec=1.0,
            )


def main():
    rclpy.init()
    node = CircleDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()