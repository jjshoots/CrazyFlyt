"""Controls 4 CrazyFlie drones hovering, can be done in either simulation or reality."""
import argparse
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
    parser = argparse.ArgumentParser(
        description="Controls 4 Crazyflie drones to hover."
    )

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
    start_states = np.array(
        [
            [0.0, -1.0, 0.05, 0.0],
            [0.0, 1.0, 0.05, 0.0],
            [-1.0, 0.0, 0.05, 0.0],
            [1.0, 0.0, 0.05, 0.0],
        ]
    )

    # spawn in a drone
    UAVs = Simulator(start_states=start_states)
    UAVs.set_pos_control(True)

    return UAVs


def real_handler():
    """real_handler."""
    URIs = []
    URIs.append("radio://0/10/2M/E7E7E7E7E2")
    URIs.append("radio://0/10/2M/E7E7E7E7E7")
    URIs.append("radio://0/30/2M/E7E7E7E7E0")
    URIs.append("radio://0/10/2M/E7E7E7E7E6")

    # connect to a drone
    UAVs = SwarmController(URIs)
    UAVs.set_pos_control(True)

    # reshuffle to optimal positions
    start_pos = np.array(
        [[0.0, -1.0, 0.05], [0.0, 1.0, 0.05], [-1.0, 0.0, 0.05], [1.0, 0.0, 0.05]]
    )
    UAVs.reshuffle(start_pos)

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
    UAVs.arm([True] * UAVs.num_drones)

    # initial hover
    UAVs.set_setpoints(
        np.array(
            [
                [0.0, -1.0, 1.0, 0.0],
                [0.0, 1.0, 1.0, 0.0],
                [-1.0, 0.0, 1.0, 0.0],
                [1.0, 0.0, 1.0, 0.0],
            ]
        )
    )
    UAVs.sleep(10)

    # send the drone back down
    UAVs.set_setpoints(
        np.array(
            [
                [0.0, -1.0, -1.0, 0.0],
                [0.0, 1.0, -1.0, 0.0],
                [-1.0, 0.0, -1.0, 0.0],
                [1.0, 0.0, -1.0, 0.0],
            ]
        )
    )
    UAVs.sleep(5)

    # stop the drone flight controller
    UAVs.arm([False] * UAVs.num_drones)
    UAVs.sleep(5)

    # end the drone control
    UAVs.end()
