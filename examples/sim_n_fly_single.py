"""Hovers one CrazyFlie drone, can be done in either simulation or reality."""
import argparse
import math
import os
from signal import SIGINT, signal

import numpy as np

from CrazyFlyt import Simulator, SwarmController


def shutdown_handler(*_):
    """shutdown_handler.

    Args:
        _: args
    """
    print("ctrl-c invoked")
    os._exit(1)


def get_args():
    """get_args."""
    parser = argparse.ArgumentParser(description="Hovers a single CrazyFlie drone.")

    parser.add_argument(
        "--simulate",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="Use simulation.",
    )

    parser.add_argument(
        "--hardware",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="Run on actual drones.",
    )

    return parser.parse_args()


def fake_handler():
    """fake_handler."""
    start_pos = np.array([[0.0, 0.0, 0.05]])
    start_orn = np.array([[0.0, 0.0, 0.0]])

    # spawn in a drone
    UAVs = Simulator(start_pos=start_pos, start_orn=start_orn)
    UAVs.set_pos_control(True)

    return UAVs


def real_handler():
    """real_handler."""
    URIs = []
    URIs.append("radio://0/10/2M/E7E7E7E7E2")

    # connect to a drone
    UAVs = SwarmController(URIs)
    UAVs.set_pos_control(True)

    return UAVs


if __name__ == "__main__":
    args = get_args()
    signal(SIGINT, shutdown_handler)

    UAVs = None
    if args.simulate:
        UAVs = fake_handler()
    elif args.hardware:
        UAVs = real_handler()
    else:
        print("Guess this is life now.")
        exit()

    # arm all drones
    UAVs.arm([True])

    # initial hover
    UAVs.set_setpoints(np.array([[0.0, 1.0, 1.0, 0.0]]))
    UAVs.sleep(10)

    # send to top of circle
    UAVs.set_setpoints(np.array([[1.0, 1.0, 1.0, 0.0]]))
    UAVs.sleep(10)

    for i in range(300):
        theta = float(i) / 10.0
        c, s = math.cos(theta), math.sin(theta)

        UAVs.set_setpoints(np.array([[c, s + 1, 1.0, 0.0]]))
        UAVs.sleep(0.1)

    # send the drone back to origin hover
    UAVs.set_setpoints(np.array([[0.0, 1.0, 1.0, 0.0]]))
    UAVs.sleep(10)

    # send the drone back down
    UAVs.set_setpoints(np.array([[0.0, 1.0, -1.0, 0.0]]))
    UAVs.sleep(5)

    # stop the drone flight controller
    UAVs.arm([False])
    UAVs.sleep(5)

    # end the drone control
    UAVs.end()
