import math

import trainer.silver_bullet as bullet
import pybullet

from .utils import dictzip

def create_scene(ts, skip):
    return bullet.Scene(gravity=9.8, timestep=ts, frame_skip=skip)

def load_urdf(scene, path, with_self_collision=True):
    if with_self_collision:
        flags = pybullet.URDF_USE_SELF_COLLISION
    else:
        flags = 0
    robot = bullet.robot.load_urdf(scene, path, flags)
    return robot

def reset_position(robot):
    robot.bring_on_the_ground()

def reset(scene, path):
    scene.episode_restart()

    robot = load_urdf(scene, path)

    reset_position(robot)

    return robot

def apply_joints(robot, positions):
    for name, pos in positions.items():
        robot.set_joint_position(name, pos, 0.1, 1.0, 100000)

