"""Virtual version of the swarm_controller or drone_controller code."""
import copy
import os
import time

import numpy as np
from PyFlyt.core import Aviary
from scipy.optimize import linear_sum_assignment


class Simulator:
    """Simulator.

    Virtual version of the swarm_controller or drone_controller code.
    Intended to be used to visualize how the real drones will fly.

    Control is done using linear velocity setpoints and yawrate:
        vx, vy, vz, vr
    States is full linear position and yaw:
        x, y, z, r
    """

    def __init__(self, start_pos: np.ndarray, start_orn: np.ndarray):
        """__init__.

        Args:
            start_pos (np.ndarray): (n, 3) array of starting positions for the drones to be spawned in
            start_orn (np.ndarray): (n, 3) array of starting orientations for the drones to be spawned in
        """
        # we use a custom drone that is accurate to the real model
        drone_options = dict()
        drone_options["model_dir"] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "./models/"
        )
        drone_options["drone_model"] = "cf2x"

        # instantiate the digital twin
        self.env = Aviary(
            drone_type="quadx",
            start_pos=start_pos,
            start_orn=start_orn,
            render=True,
            drone_options=drone_options,
        )
        self.set_pos_control(True)
        self.env.set_armed([0] * self.env.num_drones)

        # keep track of runtime
        self.steps = 0

    def reshuffle(self, new_pos):
        """reshuffle.

        Args:
            new_pos (np.ndarray): (n, 4) array for the target position to assign to all the drones
        """
        # if start pos is given, reassign to get drones to their positions automatically
        assert (
            len(new_pos) == self.num_drones
        ), "must have same number of drones as number of drones"
        assert new_pos[0].shape[0] == 4, "start pos must have only xyz"

        # compute cost matrix
        cost = abs(
            np.expand_dims(self.position_estimate[:, :3], axis=0)
            - np.expand_dims(new_pos[:, :3], axis=1)
        )
        cost = np.sum(cost, axis=-1)

        # compute optimal assignment using Hungarian algo
        _, reassignment = linear_sum_assignment(cost)
        self.env.drones = [self.env.drones[i] for i in reassignment]

        # send setpoints
        self.set_pos_control(True)
        self.set_setpoints(new_pos)

        cost = np.choose(reassignment, cost.T)
        return cost

    def set_setpoints(self, setpoints: np.ndarray):
        """set_setpoints.

        Args:
            setpoints (np.ndarray): (n, 4) array for setpoint corresponding to (x, y, z, yaw) or (vx, vy, vz, vyaw)
        """
        # the setpoints in the digital twin has the last two dims flipped
        temp = copy.deepcopy(setpoints[:, -2])
        setpoints[:, -2] = copy.deepcopy(setpoints[:, -1])
        setpoints[:, -1] = temp
        self.env.set_all_setpoints(setpoints)

    def set_pos_control(self, setting: bool):
        """set_pos_control.

        Args:
            setting (bool): whether to set all drones to pos control
        """
        self.env.set_mode(7 if setting else 6)

    def get_states(self):
        """get_states."""
        raw_states = np.array(self.env.all_states)
        states = np.zeros((self.num_drones, 4))
        states[:, :-1] = copy.deepcopy(raw_states[:, -1, :])
        states[:, -1] = copy.deepcopy(raw_states[:, 1, -1])

        return states

    def sleep(self, seconds: float | None = None):
        """sleep.

        Args:
            seconds (float | None): seconds
        """
        num_steps = 1 if seconds is None else int(seconds / self.env.update_period)

        for _ in range(num_steps):
            self.steps += 1
            self.env.step()

    def arm(self, settings: list[bool]):
        """arm.

        Args:
            settings (list[bool]): setting for arming all drones in the simulation
        """
        self.env.set_armed(settings)

    def end(self):
        """end."""
        self.arm([False] * self.num_drones)
        time.sleep(3)
        exit()

    @property
    def position_estimate(self):
        return self.get_states()

    @property
    def num_drones(self):
        """num_drones."""
        return self.env.num_drones

    @property
    def elapsed_time(self):
        """elapsed_time."""
        return self.env.physics_period * self.steps
