"""Scripted demo: known obstacles, then an unmapped obstacle, then waypoints."""
import time

import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator

from tb3_nav2_demo.send_goal import make_pose, wait_for_task
from tb3_nav2_demo.spawn_obstacle import spawn_box

START = (-2.0, -0.5, 0.0)
GOAL = (1.8, -0.5, 0.0)
BOX = (-0.55, -0.55)
WAYPOINTS = [(1.67, 1.54, 0.0), (1.8, -0.5, 0.0), (-2.0, -0.5, 0.0)]  # free spots


def go_to(navigator, label, goal):
    print(f'=== {label} ===')
    navigator.goToPose(make_pose(navigator, *goal))
    wait_for_task(navigator, label)


def main():
    rclpy.init()
    navigator = BasicNavigator('demo_runner')

    print('=== Stage 0: set initial pose, wait for Nav2 ===')
    navigator.setInitialPose(make_pose(navigator, *START))  # fallback to AMCL param
    navigator.waitUntilNav2Active()

    go_to(navigator, 'Stage 1: start -> goal across pillars', GOAL)
    go_to(navigator, 'Stage 2: back to start', START)

    print(f'=== Stage 3: spawn unmapped box at {BOX} ===')
    print('Box spawned' if spawn_box('demo_box', *BOX) else 'Box spawn FAILED')
    time.sleep(3.0)  # let the lidar see it

    go_to(navigator, 'Stage 4: start -> goal around unmapped box', GOAL)

    print('=== Stage 5: waypoint loop ===')
    navigator.followWaypoints([make_pose(navigator, *w) for w in WAYPOINTS])
    wait_for_task(navigator, 'Stage 5: waypoints')

    print('=== Demo finished ===')
    rclpy.shutdown()


if __name__ == '__main__':
    main()
