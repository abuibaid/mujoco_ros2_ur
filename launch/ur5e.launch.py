import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
import xacro


def generate_launch_description():
    # Get package paths
    mujoco_ros2_ur_path = get_package_share_directory("mujoco_ros2_ur")

    # Load and process xacro file
    xacro_file = os.path.join(
        mujoco_ros2_ur_path, "ur_description", "urdf", "ur5e", "ur5e_mujoco.urdf.xacro"
    )
    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    robot_description = {"robot_description": doc.toxml()}

    # Path to controller config
    controller_config_file = os.path.join(
        mujoco_ros2_ur_path, "config", "ur5e_controllers_mujoco.yaml"
    )
    # griiper_controller_config_file = os.path.join(mujoco_ros2_ur_path, 'config', 'robotiq_controller_mujoco.yaml')
    rviz_config_file = os.path.join(mujoco_ros2_ur_path,
                                              'launch',
                                              'camera_demo.rviz')
    # Main control node
    node_mujoco_ros2_control = Node(
        package="mujoco_ros2_control",
        executable="ros2_control_node",
        output="both",
        parameters=[
            {"use_sim_time": True},
            robot_description,
            controller_config_file,
        ],
    )

    # Robot state publisher
    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"use_sim_time": True}, robot_description],
    )

    # rviz_node = Node(
    #     package="rviz2",
    #     executable="rviz2",
    #     name="rviz2",
    #     output="screen",
    #     parameters=[{"use_sim_time": True}],
    #     arguments=["-d", rviz_config_file],
    # )


    # Controllers to spawn
    controllers = [
        "joint_state_broadcaster",
        "joint_trajectory_controller",
        "force_torque_sensor_broadcaster",
        "gripper_controller",
        "camera_position_controller",
    ]

    spawner_nodes = [
        TimerAction(
            period=4.0 + index,
            actions=[
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=[
                        controller,
                        "-c",
                        "/controller_manager",
                        "--controller-manager-timeout",
                        "30",
                        "--switch-timeout",
                        "30",
                    ],
                    output="screen",
                )
            ],
        )
        for index, controller in enumerate(controllers)
    ]

    # gripper_controllers = [
    #     "gripper_controller",

    #     "gripper_state_controller"
    # ]
    # gripper_spawner_nodes = [
    #     Node(
    #         package="controller_manager",
    #         executable="spawner",
    #         arguments=[gripper_controllers, "-c", "/robotiq/controller_manager"],
    #         output="screen"
    #     ) for gripper_controllers in gripper_controllers
    # ]
    return LaunchDescription(
        [
            node_mujoco_ros2_control,
            node_robot_state_publisher,
            # rviz_node,
            *spawner_nodes,

            # *gripper_spawner_nodes
        ]
    )
