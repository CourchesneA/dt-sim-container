FROM osrf/ros:melodic-desktop-full-bionic

RUN apt-get update \
    && apt-get install -y python3-pip python-catkin-tools  build-essential xvfb python-frozendict ffmpeg python-ruamel.yaml \
    && apt-get -y autoremove \
    && apt-get -y clean  \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install pip -U \
    && rm -r /root/.cache/pip

RUN apt-get install python3-pip
RUN pip3 install rospkg catkin_pkg pyyaml 

RUN mkdir duckietown

COPY setup/requirements.txt duckietown
COPY setup/initial.sh duckietown
RUN cd duckietown && ./initial.sh 

COPY simulation/requirements.txt duckietown
RUN  pip install -r duckietown/requirements.txt


ENV ROS_PYTHON_VERSION 3
ENV SHELL /bin/bash

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
COPY setup/requirementspy2.txt duckietown
RUN python -m pip install -r duckietown/requirementspy2.txt


WORKDIR /duckietown


RUN mkdir sim_ws
COPY sim_ws sim_ws


RUN . /opt/ros/melodic/setup.sh && \
catkin build --workspace sim_ws
COPY setup/run_display.bash .
RUN chmod u+x run_display.bash

COPY setup/launch_sim.sh .

RUN chmod u+x launch_sim.sh

CMD ./launch_sim.sh