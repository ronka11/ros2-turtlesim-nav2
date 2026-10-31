# ros2-turtlesim-nav2

Submission from: Raunak Rajput


Autonomous navigation of a TurtleBot3 (Waffle) in Gazebo Harmonic using the ROS 2 Jazzy Navigation2 (Nav2) stack. The robot crosses a field of pillars, then detects and avoids an obstacle that is not on the map. No custom navigation algorithms: this package wires up existing Nav2 components, a tuned parameter file, and a scripted demo.

**Demo video:** [Video](tb3_nav2_demo/resource/final_demo_video.mp4)

## Environment

- Host: Fedora (Wayland), ROS 2 running in a [distrobox](https://distrobox.it) container: Ubuntu 24.04, created with `--nvidia` for GPU access
- ROS 2 Jazzy, Gazebo Harmonic, Nav2

```bash
distrobox create --name ros2 --image ubuntu:24.04 --nvidia
distrobox enter ros2
# inside the container (after adding the ROS 2 apt repo, see docs.ros.org):
sudo apt install ros-jazzy-desktop ros-dev-tools ros-jazzy-ros-gz \
  ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-nav2-minimal-tb* \
  ros-jazzy-nav2-simple-commander
```

## Build and run

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/<your-user>/tb3-nav2-demo.git tb3_nav2_demo
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select tb3_nav2_demo
source install/setup.bash
```

Terminal 1 (Gazebo, RViz, Nav2). If Gazebo hangs on startup, run `export DISPLAY=:0` first (see challenge 7):

```bash
ros2 launch tb3_nav2_demo demo.launch.py
```

Terminal 2 (scripted demo, once Nav2 has started):

```bash
ros2 run tb3_nav2_demo demo_runner --ros-args -p use_sim_time:=True
```

Launch arguments: `headless:=True` (no Gazebo GUI), `use_composition:=True`, `params_file:=...`.

Standalone tools:

```bash
# send one goal (defaults: x=1.8 y=-0.5 yaw=0.0)
ros2 run tb3_nav2_demo send_goal --ros-args -p use_sim_time:=True -p x:=1.67 -p y:=1.54

# drop the unmapped box into the running world (defaults: demo_box, -0.55, -0.55)
ros2 run tb3_nav2_demo spawn_obstacle --ros-args -p x:=-0.55 -p y:=-0.55
```

## How it works

- Gazebo simulates the robot and world; the `ros_gz` bridge publishes `/scan`, `/odom`, `/tf` and `/clock`.
- `map_server` serves the pre-built map; AMCL localizes against it and publishes `map -> odom`.
- TF chain: `map -> odom -> base_link -> base_scan`.
- The BT Navigator handles the `navigate_to_pose` action, calling the planner (global costmap) and the controller (local costmap).
- Costmap layers: static (map), obstacle (lidar), inflation (safety margin).

## What the demo shows

1. Navigation around **known** obstacles: the pillars come from the static map layer.
2. Detection and avoidance of an **unmapped** obstacle: a 0.3 x 0.3 x 0.5 m box is spawned at (-0.55, -0.55), blocking the straight route. The lidar marks it in the obstacle layer, and Nav2 replans through another gap.

`demo_runner` stages: initial pose, start to goal, back to start, spawn box, start to goal again (around the box), then a short waypoint loop. Each stage prints a one-line status.

## Configuration changes

`config/nav2_params.yaml` is a copy of Jazzy's `nav2_params.yaml`.

| Parameter | Change | Why |
|---|---|---|
| `amcl.set_initial_pose`, `amcl.initial_pose` | `true`, (-2.0, -0.5, yaw 0) | AMCL needs an initial pose to publish `map -> odom`; removes the manual "2D Pose Estimate" click |
| `controller_server.FollowPath.batch_size` (MPPI) | 2000 -> 1000 | Lower CPU load; the 20 Hz control loop was missing its rate |

## Challenges and how I solved them

I'm new to ROS 2, so I solved most of these by reading logs, searching online, and working through them with AI help. I've tried to explain what I understood about each one.

1. **Nav2 wouldn't start ("inactive", then "Node not found").**
   Nav2 is made of many small programs (nodes). A "lifecycle manager" starts them one by one, and if any one of them fails, it stops everything. By default, all these nodes ran inside one single process, so when one crashed, it took everything down with it. Running with `use_composition:=False` puts each node in its own process, so one crash doesn't kill the rest, and the logs show which node failed.

2. **Clicking "Nav2 Goal" did nothing.**
   The robot didn't know where it was on the map yet. AMCL (the part that works out the robot's position) needs a starting guess. Without it, Nav2 can't plan a path. I gave it one with the "2D Pose Estimate" button in RViz, and later set the starting position in the config file so it happens automatically.

3. **The Gazebo window was empty, or opening it made Nav2 crash.**
   My ROS setup runs inside a container (distrobox), and the container couldn't use my NVIDIA graphics card. So Gazebo drew the 3D view with the CPU instead, which slowed the whole computer down enough for Nav2 to fail. At first I ran Gazebo without its window ("headless"). The real fix was making a new container with GPU access (`--nvidia`).

4. **Copying my container into a GPU-enabled one got stuck.**
   I tried to save my existing container and make a GPU version from it. It froze. The verbose log showed the saved copy was trying to run a startup script that never finishes. Fixing that got me one step further, but it got stuck again at a later step. Instead of spending more time on it, I made a fresh Ubuntu container with GPU access, checked the GPU worked first, and reinstalled ROS.

5. **"Control loop missed its desired rate" warnings.**
   The part of Nav2 that steers the robot (the controller) is supposed to update 20 times per second, but with Gazebo also running, my laptop couldn't always keep up. I lowered how many possible paths the controller tests each update (`batch_size`), which reduced the load.

6. **Gazebo sometimes crashed at startup, so the robot never appeared.**
   The launch file creates the world file and starts Gazebo at the same time, so sometimes Gazebo started before the world file was ready. My launch file now waits for the world file to be created before starting Gazebo.

7. **Gazebo got stuck while loading and never opened.**
   This turned out to be a display setting. The `DISPLAY` variable tells programs which screen to draw on. My VS Code terminal had it set to `:3`, but my actual screen is `:0`. Setting `export DISPLAY=:0` before launching fixed it. An earlier error, where turtlesim couldn't open its window, was probably the same kind of problem, so now I check `DISPLAY` first when a window won't open.

8. **Small issues.**
   RViz shows an error for the robot's 3D model files. It's only visual; turning on the collision display shows the robot's shape instead. Also, the first `ros2` command in a new terminal sometimes says "Node not found" because it hasn't found the other nodes yet; running it again works.

## What I learned

- **How ROS 2 programs talk to each other:**
  - **Topics** are continuous streams of data, like laser scans or speed commands.
  - **Services** are quick one-off requests.
  - **Actions** are longer tasks, like "drive to this point", which give progress updates and end as succeeded, canceled or aborted.
  - **Parameters** are settings.
- **Nav2 starts its parts in a fixed order,** and if one fails, the rest don't start. Checking each node's state helped me find what was broken.
- **How the robot knows where it is:** wheel odometry tracks movement but slowly drifts. AMCL compares the laser scan to the map to correct that drift.
- **How Nav2 moves the robot:** a planner draws a path across the whole map, and a controller steers along it while watching nearby obstacles. The robot doesn't follow the line exactly, and it stops when it's close enough to the goal.
- **Costmaps:** Nav2 combines the saved map, what the laser sees right now, and a safety zone around obstacles. That's how it avoided a box that wasn't on the map.
- **Simulation time:** all nodes need `use_sim_time` so they follow Gazebo's clock instead of the computer's clock.
- **Building packages:** how a ROS 2 package is structured, building with colcon, and reusing Nav2's launch files with my own settings.
- **Debugging:** save logs to a file and search them, change one thing at a time, and check basics like the GPU and display settings before assuming ROS is broken.


## Resources

- [Official ROS 2 Jazzy documentation](https://docs.ros.org/en/jazzy/)
- [Nav2 documentation](https://docs.nav2.org/)
- [Learn ROS 2: Beginner to Advanced Course (Concepts and Code) – Kevin Wood | Robotics & AI](https://www.youtube.com/watch?v=HJAE5Pk8Nyw)
- [Making robot navigation easy with Nav2 and ROS! – Articulated Robotics](https://www.youtube.com/watch?v=jkoGkAd0GYk)
- [Articulated Robotics (YouTube channel)](https://www.youtube.com/@ArticulatedRobotics/videos)
