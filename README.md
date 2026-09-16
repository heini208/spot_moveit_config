# Spot MoveIt configuration (ROS 2 Humble)

Based on `/home/marcel/Projects/spot/spot_with_arm.urdf`, with a fixed SDK `hand` frame added.
Requires the matching `spot_description` package for meshes.

## Build and run when ready

```bash
source /opt/ros/humble/setup.bash
cd /home/marcel/Projects/spot/spot_ws
source install/setup.bash
colcon build --packages-select spot_moveit_config
source install/setup.bash
ros2 launch spot_moveit_config demo.launch.py
```

This starts a standalone preview with synthetic joint states, robot state publisher,
MoveIt and RViz. Run separately from the real driver to avoid joint-state/TF conflicts.
Select `arm` in MotionPlanning, move the goal marker and use **Plan**.
Execution is disabled. No robot controller or SDK connection is configured.

## Model choices and limits

- `arm`: six active joints, from `body` to `hand`, using KDL IK and OMPL RRTConnect.
  The collision-less `hand` frame is 0.19557 m along wrist X with the same orientation,
  matching Spot SDK hand-pose targets. It is not a calibrated tool/contact point.
- `gripper`: `arm_f1x`, with open/closed targets, physically attached to the wrist.
- Body is the fixed planning frame. Legs are passive and retain collision geometry.
  This does not plan locomotion or body movement.
- Only adjacent links are excluded from collision checking. No sampled self-collision
  matrix has been generated. Initial positions are illustrative and within joint bounds,
  but have not been verified collision-free. Review collision contacts before disabling
  any additional pairs.
- Planning velocity and acceleration caps are 0.5 rad/s and 0.5 rad/s² with 0.1 scaling.
  These are preview settings, not manufacturer-validated hardware limits.
- SH1 planning bounds in `config/joint_limits.yaml` are -2.96706 rad (about -170°)
  to 0.5235987755982988 rad (30°). The lower bound provides a project-specific
  10° software planning margin above the physical -pi limit; it is not a Boston
  Dynamics hardware limit. It was chosen because the reported false-contact
  trajectory reached about -3.126 rad (-179.1°). The margin may be reduced later
  if it unnecessarily limits reachability. The URDF hardware bounds are unchanged.
- Hardware execution requires a verified trajectory controller/Spot SDK bridge and
  live state/TF integration. The URDF alone does not provide that interface.
  The existing `probe()` executor sends SDK hand-pose commands directly; these MoveIt
  limits do not constrain that path until MoveIt planning is integrated.

Static validation only: no nodes, Setup Assistant, robot connection or deployment
were started. The reported Setup Assistant crash has not been reproduced or diagnosed.

Configuration references:
https://dev.bostondynamics.com/docs/concepts/arm/arm_concepts.html#hand-frame
https://moveit.picknik.ai/humble/doc/examples/kinematics_configuration/kinematics_configuration_tutorial.html
https://moveit.picknik.ai/humble/doc/examples/ompl_interface/ompl_interface_tutorial.html
