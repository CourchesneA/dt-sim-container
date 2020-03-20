#!/usr/bin/env python3


import logging
import signal
import sys
import time
import os


import numpy as np

from zuper_nodes_wrapper.wrapper_outside import ComponentInterface, MsgReceived
from aido_schemas import protocol_agent_duckiebot1

if '/duckietown/simulation/src' not in sys.path:
    sys.path.append('/duckietown/simulation/src')

logger = logging.getLogger('SimulatorBridge')
logger.setLevel(logging.DEBUG)


class SimulatorBridge(object):
    """
    bridges the communication between the FIFOs and the simulator
    """
    def __init__(self):
        # We should remove /fifos/agen-in if present
        logger.info("Initialized simbridge")
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        self.vehicle = os.getenv('HOSTNAME')
        self.action = np.array([0.0, 0.0])
        self.updated = True

        self.rate = 15


    def exit_gracefully(self, signum, frame):
        logger.info('SimulatorBridge exiting gracefully.')
        sys.exit(0)

    def run(self):
        stepnum = 0
        env = launch_env()
        obs = env.reset()
        #print("Environment launched")

        logger.info('DuckiebotBridge has created Simulator environment')

        while True:

            # get actions from pipes

            time.sleep(1 / self.rate)

            obs, reward, done, _ = env.step(self.action)

            stepnum+=1
            if done:
                obs = env.reset()

            np_arr = np.fromstring(obs, np.uint8)
            data = np_arr.tostring()

            if stepnum % 20 == 0:
                logger.info("{} steps done".format(stepnum))
            if stepnum == 100000:
                stepnum = 0
            


def main():
    node = SimulatorBridge()
    #print("starting DuckiebotBridge node")
    node.run()
    # at rate 15, should set action, step, publisg img and reset if done

def launch_env(simclass=None):
    #print(sys.path)
    #TODO local sim and remove path change in beginning
    from simulation.src.gym_duckietown.simulator import Simulator

    simclass = Simulator if simclass is None else simclass

    env = simclass(
        seed=4, # random seed
        map_name="loop_empty",
        max_steps=500001, # we don't want the gym to reset itself
        domain_rand=0,
        camera_width=640,
        camera_height=480,
        accept_start_angle_deg=4, # start close to straight
        full_transparency=True,
        distortion=True,
    )   
    return env 


if __name__ == '__main__':
    main()
