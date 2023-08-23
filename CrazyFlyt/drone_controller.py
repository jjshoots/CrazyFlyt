"""Class for controlling a single Crazyflie UAV."""
import math
import threading
import time

import cflib.crtp
import numpy as np
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
# from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper


class DroneController:
    """DroneController.

    Class for controlling a single Crazyflie UAV.
    """

    def __init__(self, URI, in_swarm=False):
        """__init__.

        Args:
            URI: URI of the drone
            in_swarm: whether the drone is operating in a swarm, this just adds a delay before initialization.
        """
        self.period = 1 / 40.0
        URI = uri_helper.uri_from_env(default=URI)

        self.running = False
        self.flow_deck_attached = False

        self.position_estimate = np.array([0.0, 0.0, 0.0, 0.0])
        self.setpoint = np.array([0.0, 0.0, 0.0, 0.0])

        self.pos_control = False
        self.rad_to_deg = np.array([1.0, 1.0, 1.0, math.pi / 180.0])

        # make connection
        self.scf = None
        try:
            cflib.crtp.init_drivers()
            self.scf = SyncCrazyflie(URI, cf=Crazyflie(rw_cache="./cache"))
            self.scf.open_link()
        except Exception as e:
            print(f"Failed to open link with Flier on {URI}, {e}.")

        # update the onboard PIDs
        # self.param_set("posCtlPid", "xKp", 1.2)
        # self.param_set("posCtlPid", "yKp", 1.2)
        # self.param_set("posCtlPid", "zKp", 1.0)
        # self.param_set("posCtlPid", "zKi", 0.2)

        # logging thread
        self.logging_thread = LogConfig(name="Position", period_in_ms=10)
        self.logging_thread.add_variable("stateEstimate.x", "float")
        self.logging_thread.add_variable("stateEstimate.y", "float")
        self.logging_thread.add_variable("stateEstimate.z", "float")
        self.logging_thread.add_variable("stateEstimate.yaw", "float")
        self.scf.cf.log.add_config(  # pyright: ignore [reportOptionalMemberAccess] # noqa: E501
            self.logging_thread
        )
        self.logging_thread.data_received_cb.add_callback(self._log_callback)

        # start the logging thread automatically
        self.logging_thread.start()

        # start drone control automatically
        self.control_thread = threading.Thread(name="background", target=self._control)
        self.control_thread.setDaemon(True)
        self.control_thread.start()

        # delay a bit to let things stabilize if not in swarm
        print(f"Flier on {URI} ready to rock and roll...")
        if not in_swarm:
            time.sleep(3)

    def start(self):
        """Start the drone."""
        self.running = True

    def stop(self):
        """Stop the drone."""
        self.running = False

    def end(self):
        """Stops the drone and closes all connections."""
        self.running = False
        self.logging_thread.stop()
        self.scf.close_link()  # pyright: ignore [reportOptionalMemberAccess]

    def set_pos_control(self, setting):
        """set_pos_control.

        Args:
            setting (bool): whether to set all drones to pos control
        """
        self.pos_control = setting

    def set_setpoint(self, setpoint: np.ndarray):
        """set_setpoint.

        Args:
            setpoint (np.ndarray): (4, ) array for setpoint corresponding to (x, y, z, yaw) or (vx, vy, vz, vyaw)
        """
        self.setpoint = setpoint

    def sleep(self, seconds: float):
        """sleep.

        Args:
            seconds (float): seconds
        """
        time.sleep(seconds)

    def _control(self):
        """_control."""
        while True:
            if self.running:
                if self.pos_control:
                    self.scf.cf.commander.send_position_setpoint(  # pyright: ignore [reportOptionalMemberAccess]
                        *(self.setpoint * self.rad_to_deg)
                    )
                else:
                    self.scf.cf.commander.send_velocity_world_setpoint(  # pyright: ignore [reportOptionalMemberAccess]
                        *(self.setpoint * self.rad_to_deg)
                    )
            else:
                self.scf.cf.commander.send_stop_setpoint()  # pyright: ignore [reportOptionalMemberAccess]

            time.sleep(self.period)

    def _log_callback(self, timestamp, data, logconf):
        """_log_callback.

        Args:
            timestamp: timestamp
            data: data
            logconf: logconf
        """
        # """logging callback, NOT to be called in main"""
        self.position_estimate[0] = data["stateEstimate.x"]
        self.position_estimate[1] = data["stateEstimate.y"]
        self.position_estimate[2] = data["stateEstimate.z"]
        self.position_estimate[3] = data["stateEstimate.yaw"] / 180.0 * math.pi

    def _update_param_callback(self, name, value):
        """_update_param_callback.

        Args:
            name: name
            value: value
        """
        print(f"The CrazyFlie has parameter {name} set to {value}.")
        pass

    def param_set(self, groupstr, namestr, value):
        """param_set.

        Args:
            groupstr:  groupstr
            namestr: namestr
            value: value
        """
        full_name = groupstr + "." + namestr

        self.scf.cf.param.add_update_callback(  # pyright: ignore [reportOptionalMemberAccess] # noqa: E501
            group=groupstr, name=namestr, cb=self._update_param_callback
        )
        time.sleep(1)
        self.scf.cf.param.set_value(  # pyright: ignore [reportOptionalMemberAccess] # noqa: E501
            full_name, value
        )
