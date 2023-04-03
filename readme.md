# CrazyFlyt

# This library very much in the developmental stage

This is a library for flying real CrazyFlie 2.x drones with support for a simulation environment via the [PyFlyt](https://github.com/jjshoots/PyFlyt) library.
Example scripts are provided under `examples/***.py`.

The library is built using CrazyFlie drones, check out the [documentation](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyflie-2-x/).

### Simulation Only

#### `sim_single.py`
Simulates a single drone in the pybullet env with position control.
<p align="center">
    <img src="/readme_assets/simulate_single.gif" width="500px"/>
</p>

#### `sim_swarm.py`
Simulates a swarm of drones in the pybullet env with velocity control.
<p align="center">
    <img src="/readme_assets/simulate_swarm.gif" width="500px"/>
</p>

#### `sim_cube.py`
Simulates a swarm of drones in a spinning cube.
<p align="center">
    <img src="/readme_assets/simulate_cube.gif" width="500px"/>
</p>

### Hardware Only

#### `fly_single.py`
Flies a real Crazyflie, check out the [documentation](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyflie-2-x/) and [how to connect](https://www.bitcraze.io/documentation/tutorials/getting-started-with-crazyflie-2-x/#config-client) to get your URI(s) and modify them in line 18.

#### `fly_swarm.py`
Flies a real Crazyflie swarm, same as the previous example, but now takes in a list of URIs.

### Simulation or Hardware

#### `sim_n_fly_single.py`
Simple script that can be used to fly a single crazyflie in sim or with a real drone using either the `--hardware` or `--simulate` args.

#### `sim_n_fly_multiple.py`
Simple script that can be used to fly a swarm of crazyflies in sim or with real drones using either the `--hardware` or `--simulate` args.

#### `sim_n_fly_cube_from_scratch.py`
Simple script that can be used to fly a swarm of crazyflies in sim or with real drones using either the `--hardware` or `--simulate` args, and forms the same spinning cube from takeoff as in `sim_cube.py`.

