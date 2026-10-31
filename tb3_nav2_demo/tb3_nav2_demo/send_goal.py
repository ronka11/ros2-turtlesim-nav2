"""Send a single NavigateToPose goal and report progress and result."""
import math
import time

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator


def make_pose(navigator, x, y, yaw):
    """Build a PoseStamped in the map frame from x, y (m) and yaw (rad)."""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def wait_for_task(navigator, label):
    """Wait for the running Nav2 task, print progress, return its result."""
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        # Waypoint feedback has no distance_remaining, so check first.
        if feedback and hasattr(feedback, 'distance_remaining'):
            print(f'[{label}] distance remaining: {feedback.distance_remaining:.2f} m')
        time.sleep(1.0)
    result = navigator.getResult()  # SUCCEEDED, CANCELED or FAILED
    print(f'[{label}] result: {result.name}')
    return result


def main():
    rclpy.init()
    navigator = BasicNavigator('send_goal')
    x = navigator.declare_parameter('x', 1.8).value
    y = navigator.declare_parameter('y', -0.5).value
    yaw = navigator.declare_parameter('yaw', 0.0).value

    navigator.waitUntilNav2Active()
    navigator.goToPose(make_pose(navigator, x, y, yaw))
    wait_for_task(navigator, f'goal ({x}, {y})')
    rclpy.shutdown()


if __name__ == '__main__':
    main()
