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
        print("Init simbridge")
        logger.info("Initialized simbridge")
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        self.vehicle = os.getenv('HOSTNAME')
        self.action = np.array([0.0, 0.0])
        self.updated = True

        self.rate = 15


        print("About to connect fifos")
        logger.info("Starting fifos connection")
        AIDONODE_DATA_IN = '/fifos/agent-in'
        AIDONODE_DATA_OUT = '/fifos/agent-out'
        
        if os.path.exists(AIDONODE_DATA_IN):
            logger.info(f"name pipe '{AIDONODE_DATA_IN}' already exists, deleting ...")
            os.remove(AIDONODE_DATA_IN)
            logger.info(f"{AIDONODE_DATA_IN} deleted.")

        self.ci = ComponentInterface(AIDONODE_DATA_IN,
                AIDONODE_DATA_OUT, protocol_agent_duckiebot1, 'agent', timeout=30)
        # File not found error -> problem mounting volume
        # File exist error -> volumes not properly cleaned
        self.ci.write_topic_and_expect_zero(u'seed', 32)
        self.ci.write_topic_and_expect_zero(u'episode_start', {u'episode_name': u'episode'})
        logger.info('SimulatorBridge successfully sent to the agent the seed and episode name.')
        print("Succesfully connected fifos")


    def _send_img(self, obs):
        """ img is JPEG format, send it on the FIFO"""

        contig = cv2.cvtColor(np.ascontiguousarray(obs), cv2.COLOR_BGR2RGB)
        # compatible with ROS CompressedImage
        img_data = np.array(cv2.imencode('.jpg', contig)[1]).tostring()
        obs = {u'camera': {u'jpg_data': img_data}}
        self.ci.write_topic_and_expect_zero(u'observations', obs)

    def _get_commands(self):
        commands = self.ci.write_topic_and_expect(u'get_commands', expect=u'commands')
        commands = commands.data[u'wheels']
        return commands

    def exit_gracefully(self, signum, frame):
        logger.info('SimulatorBridge exiting gracefully.')
        sys.exit(0)

    def run(self):
        env = launch_env()
        obs = env.reset()
        self._send_img(obs)
        print("Environment launched")

        logger.info('DuckiebotBridge has created Simulator environment')

        while True:

            # get actions from pipes

            time.sleep(1 / self.rate)

            action = self._get_commands()

            obs, reward, done, _ = self.env.step(action)

            if done:
                obs = env.reset()

            np_arr = np.fromstring(obs, np.uint8)
            data = np_arr.tostring()
            
            self._send_img(obs)

            vl = commands['motor_left']
            vr = commands['motor_right']
            self.action = np.array([vl,vr])
            self.updated = True

            # TODO
            # Open pipes
            # Test


def main():
    node = SimulatorBridge()
    print("starting DuckiebotBridge node")
    node.run()
    # at rate 15, should set action, step, publisg img and reset if done

def launch_env(simclass=None):
    #print(sys.path)
    #TODO local sim and remove path change in beginning
    from gym_duckietown.simulator import Simulator

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
