import os
from os import pathsep
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    bot_description = get_package_share_directory("ugv_description")

    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(bot_description, "urdf", "bot.urdf.xacro"),
        description="Absolute path to robot urdf file"
    )

    model_path = str(Path(bot_description).parent.resolve())
    model_path += pathsep + os.path.join(bot_description, 'models')

    gazebo_resource_path = SetEnvironmentVariable(
        name="GAZEBO_MODEL_PATH",
        value=model_path
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

    joint_state_pub = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic", "robot_description",
            "-entity", "ugv",
            "-x", "0.0", "-y", "2.0", "-z", "0.0"
        ],
        output="screen"
    )

    return LaunchDescription([
        model_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        joint_state_pub,
        spawn_entity,
    ])
