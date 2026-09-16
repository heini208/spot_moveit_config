"""Standalone planning preview; trajectory execution is disabled."""
from pathlib import Path
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config = Path(get_package_share_directory("spot_moveit_config")) / "config"
    def read_yaml(name):
        return yaml.safe_load((config / name).read_text())
    description = {"robot_description": (config / "spot.urdf").read_text()}
    params = {
        **description,
        "robot_description_semantic": (config / "spot.srdf").read_text(),
        "robot_description_kinematics": read_yaml("kinematics.yaml"),
        "robot_description_planning": read_yaml("joint_limits.yaml"),
        "planning_pipelines": ["ompl"],
        "default_planning_pipeline": "ompl",
        "ompl": read_yaml("ompl_planning.yaml"),
        "allow_trajectory_execution": False,
        "publish_robot_description": True,
        "publish_robot_description_semantic": True,
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
    }
    return LaunchDescription([
        DeclareLaunchArgument("rviz", default_value="true"),
        Node(package="robot_state_publisher", executable="robot_state_publisher",
             parameters=[description], output="screen"),
        Node(package="joint_state_publisher", executable="joint_state_publisher",
             parameters=[description, {"zeros": read_yaml("initial_positions.yaml")}],
             output="screen"),
        Node(package="moveit_ros_move_group", executable="move_group",
             parameters=[params], output="screen"),
        Node(package="rviz2", executable="rviz2", parameters=[params],
             arguments=["-d", str(config / "moveit.rviz")],
             condition=IfCondition(LaunchConfiguration("rviz")), output="screen"),
    ])
