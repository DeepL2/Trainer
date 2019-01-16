import numpy as np
import quaternion

import math

from .utils import select_location, select_rotation
from .simulation import reset, apply_joints
from .silver_bullet import Scene


def calc_reward(motion, robot, frame):
    diff = 0
    for name, effector in frame.effectors.items():
        pose = robot.link_state(name).pose
        root_pose = robot.link_state(robot.root_link).pose
        weight = motion.effector_weight(name)
        ty = motion.effector_type(name)
        if effector.location:
            target = select_location(ty.location, effector.location.vector, root_pose)
            diff += np.linalg.norm(pose.vector - np.array(target)) ** 2 * weight.location
        if effector.rotation:
            target = select_rotation(ty.rotation, effector.rotation.quaternion, root_pose)
            quat1 = np.quaternion(*target)
            quat2 = np.quaternion(*pose.quaternion)
            diff += quaternion.rotation_intrinsic_distance(quat1, quat2) ** 2 * weight.rotation
    k = 1
    normalized = k * diff / len(frame.effectors)
    return - math.exp(normalized) + 1


def evaluate(motion, robot_file, timestep=0.0165/8, frame_skip=8, loop=2):
    scene = Scene(timestep, frame_skip)

    robot = reset(scene, robot_file)

    reward_sum = 0
    for t, frame in motion.frames(scene.dt):
        apply_joints(robot, frame.positions)

        scene.step()

        reward_sum += calc_reward(motion, robot, frame)

        if t > motion.length() * loop:
            break

    return reward_sum
