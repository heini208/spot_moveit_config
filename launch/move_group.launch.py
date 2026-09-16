"""MoveIt planning server for the real Spot driver.

This launch starts only move_group. It consumes the live /joint_states and TF
published by the Spot ROS 2 stack and never starts synthetic state publishers or
trajectory controllers.
"""

from pathlib import Path

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def _read_yaml(config_dir: Path, name: str):
    return yaml.safe_load((config_dir / name).read_text())


def generate_launch_description():
    config_dir = Path(
        get_package_share_directory("spot_moveit_config")
    ) / "config"

    robot_description = {
        "robot_description": (config_dir / "spot.urdf").read_text()
    }

    move_group_parameters = {
        **robot_description,
        "robot_description_semantic": (
            config_dir / "spot.srdf"
        ).read_text(),
        "robot_description_kinematics": _read_yaml(
            config_dir,
            "kinematics.yaml",
        ),
        "robot_description_planning": _read_yaml(
            config_dir,
            "joint_limits.yaml",
        ),
        "planning_pipelines": ["ompl"],
        "default_planning_pipeline": "ompl",
        "ompl": _read_yaml(
            config_dir,
            "ompl_planning.yaml",
        ),
        "allow_trajectory_execution": False,
        "moveit_manage_controllers": False,
        "publish_robot_description": True,
        "publish_robot_description_semantic": True,
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
    }

    return LaunchDescription([
        Node(
            package="moveit_ros_move_group",
            executable="move_group",
            name="move_group",
            output="screen",
            parameters=[move_group_parameters],
        ),
    ])
