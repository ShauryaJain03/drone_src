import os
from os import pathsep
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    bot_description = get_package_share_directory("ugv_description")

    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(bot_description, "urdf", "bot.urdf.xacro"),
        description="Absolute path to robot urdf file"
    )

    # Set GAZEBO_MODEL_PATH for Gazebo Classic
    model_path = str(Path(bot_description).parent.resolve())
    model_path += pathsep + os.path.join(get_package_share_directory("ugv_description"), 'models')

    gazebo_resource_path = SetEnvironmentVariable(
        "GAZEBO_MODEL_PATH",
        model_path
    )

    robot_description = ParameterValue(Command([
        "xacro ",
        LaunchConfiguration("model")
    ]), value_type=str)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output='screen',
        parameters=[{"robot_description": robot_description,
                     "use_sim_time": True}]
    )

    world_name_arg = DeclareLaunchArgument(
        name="world_name", 
        default_value="empty.world",
        description="Name of the Gazebo world file"
    )

    # Fixed world path construction using PathJoinSubstitution
    world_path = PathJoinSubstitution([
        bot_description,
        "worlds",
        LaunchConfiguration("world_name")
    ])

    joint_state_pub = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # Include the standard Gazebo Classic launch file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py"
            )
        ]),
        launch_arguments={
            'world': world_path,
            'verbose': 'true'
        }.items()
    )

    # Spawn the robot into Gazebo Classic
    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic", "robot_description",
            "-entity", "bot",
            "-z", "4.0"  # Adjust initial Z position as needed
        ],
        output="screen"
    )

    return LaunchDescription([
        model_arg,
        world_name_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        joint_state_pub,
        gazebo,
        spawn_entity,
    ])