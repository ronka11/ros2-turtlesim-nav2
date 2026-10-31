"""Launch the TurtleBot3 + Nav2 demo using Nav2's own bringup with our params."""
import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess,
                            IncludeLaunchDescription, RegisterEventHandler)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression


def generate_launch_description():
    pkg_share = get_package_share_directory('tb3_nav2_demo')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    sim_dir = get_package_share_directory('nav2_minimal_tb3_sim')

    # Launch arguments exposed by this package.
    params_file = LaunchConfiguration('params_file')
    use_composition = LaunchConfiguration('use_composition')
    headless = LaunchConfiguration('headless')

    declare_args = [
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_share, 'config', 'nav2_params.yaml'),
            description='Nav2 parameters file (this package\'s tuned copy)'),
        # False: one process per Nav2 node, so logs show which node failed.
        DeclareLaunchArgument(
            'use_composition', default_value='False',
            description='Run Nav2 nodes in a single composed process'),
        # False: show the Gazebo GUI.
        DeclareLaunchArgument(
            'headless', default_value='False',
            description='Run Gazebo without the GUI (gzclient)'),
    ]

    # Reuse Nav2's TurtleBot3 simulation (robot spawn, ros_gz bridge, map_server, AMCL, Nav2, RViz)
    tb3_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'tb3_simulation_launch.py')),
        launch_arguments={
            'params_file': params_file,
            'use_composition': use_composition,
            'headless': headless,
            'use_simulator': 'False',    # start Gazebo ourselves below
        }.items())

    # Gazebo starts only after xacro writes the world file (Nav2's own launch races them).
    world_sdf = tempfile.mktemp(prefix='tb3_demo_world_', suffix='.sdf')
    world_xacro = ExecuteProcess(
        cmd=['xacro', '-o', world_sdf, ['headless:=', headless],
             os.path.join(sim_dir, 'worlds', 'tb3_sandbox.sdf.xacro')])

    gazebo_server = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-s', world_sdf], output='screen')

    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')),
        condition=IfCondition(PythonExpression(['not ', headless])),
        launch_arguments={'gz_args': '-v4 -g '}.items())

    start_gazebo_after_xacro = RegisterEventHandler(OnProcessExit(
        target_action=world_xacro,
        on_exit=[gazebo_server, gazebo_client]))

    return LaunchDescription(
        declare_args + [world_xacro, start_gazebo_after_xacro, tb3_sim])
