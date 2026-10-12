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
The demo restores the stock jaw collision shapes in its local robot description.
Select `arm` in MotionPlanning, move the goal marker and use **Plan**.
Execution is disabled. No robot controller or SDK connection is configured.

## Sensor mount collision geometry

The production `move_group.launch.py` uses an exchangeable jaw model. Its fixed,
collisionless `sensor_head_slot` is at the SDK `hand` origin. The three forward
jaw collision meshes (`front_jaw`, `middle_jaw`, `jaw_tooth`) are supplied at runtime
as one attached collision object by `fault_detector_spot`; the wrist, rear housing,
and moving finger retain their original collision geometry. The production launch
also publishes the identity `hand -> sensor_head_slot` static TF so the occupancy
self-filter can resolve attached shapes. The driver remains the owner of live
`hand` and arm TF; the standalone demo obtains the slot TF from its own robot
state publisher.

Before each arm plan, the application installs and verifies either the confirmed
sensor mount's saved mesh or the stock jaw for a confirmed **No sensor** state.
The environment toggle applies to the mount too. Use the application's planning
path with this production model; starting `move_group` alone does not populate
the jaw slot. Other planning clients must coordinate with its scene owner.

The application's `config/arm_collision.rviz` planning-scene display shows the
installed attachment after the application confirms the mount and synchronizes
the scene while the arm is idle; no movement request is needed. The application
API and BT runtime must be running as well as MoveIt. Ordinary robot visual
geometry still shows the stock gripper. The standalone demo retains the stock collision
model and does not support swapping sensor heads.

The production server publishes its URDF and SRDF on
`/spot_moveit_robot_description` and `/spot_moveit_robot_description_semantic`.
The application's collision viewer selects this paired model using its
`Robot Description: spot_moveit_robot_description` setting. The driver's generic
`/robot_description` lacks the planning-specific hand and jaw-slot links and must
not be combined with MoveIt's SRDF. Server parameter names remain
`robot_description` and `robot_description_semantic` for planning and model queries.

Rebuild `spot_moveit_config`, `fault_detector_msgs`, and `fault_detector_spot`
together before the next application startup. This change requires the new model
to be loaded once; later mount changes use planning-scene updates.

## Model choices and limits

The four hips use closed convex collision meshes generated from the matching
`spot_description` visual meshes. The upper-arm collision mesh contains both
`arm_link_sh1` and `arm_link_hr0` visuals and the original collision envelope.
These two links have an identity fixed joint, so their shared collision geometry
remains on `arm_link_hr0`. The warning that `arm_link_sh1` has no collision of its
own is expected; adding a duplicate there is unnecessary.

The meshes preserve the source frames and enclose the supplied geometry, including
its recesses. They are conservative approximations of the model, not a measured
accuracy guarantee for the physical robot. Joint transforms, collision permissions,
sensor-tip calibration, and the application's lidar filtering margins are unchanged.

To regenerate these assets offline (requires Python, NumPy and SciPy):

```bash
python3 tools/generate_collision_meshes.py --source "$(ros2 pkg prefix spot_description)/share/spot_description"
```

Add `--check` to verify the checked-in files without rewriting them. Generated
files record their input paths and checksums; their source license is included
in `config/collision/LICENSE`.

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
