#FROM osrf/ros:melodic-desktop-full-bionic
FROM duckietown/aido3-base-python3:daffy
# TODO rm ROS

RUN apt-get update \
    && apt-get install -y python3-pip build-essential xvfb python-frozendict ffmpeg python-ruamel.yaml freeglut3-dev vim \
    && apt-get -y autoremove \
    && apt-get -y clean  \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install pip -U \
    && rm -r /root/.cache/pip

#RUN apt-get install python3-pip
#RUN pip3 install rospkg catkin_pkg pyyaml 

RUN mkdir duckietown

WORKDIR /duckietown

COPY requirements.txt .
RUN pip install -r requirements.txt
#COPY setup/initial.sh duckietown
#RUN cd duckietown && ./initial.sh 

#COPY simulation/requirements.txt duckietown
#RUN  pip install -r duckietown/requirements.txt

# Custom
COPY simulation/ simulation
RUN pip install -r simulation/requirements.txt

#TODO merge those requirements ^^
#RUN pip install -r duckietown/requirements.txt

#COPY utils/ duckietown/utils

ENV ROS_PYTHON_VERSION 3
ENV SHELL /bin/bash

#RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
#RUN python get-pip.py
#COPY setup/requirementspy2.txt duckietown
#RUN python -m pip install -r duckietown/requirementspy2.txt





#RUN mkdir sim_ws
#COPY sim_ws sim_ws

COPY sim_bridge.py sim_bridge.py
COPY launch.sh launch.sh
RUN chmod +x launch.sh
COPY check_hw.sh check_hw.sh
RUN chmod +x check_hw.sh

#RUN . /opt/ros/melodic/setup.sh && \
#catkin build --workspace sim_ws
#COPY setup/run_display.bash .
#RUN chmod u+x run_display.bash

#COPY setup/launch_sim.sh .

#RUN chmod u+x launch_sim.sh

#CMD ./launch_sim.sh
#CMD python3 ./sim_bridge.py
#CMD ./launch.sh
ENTRYPOINT ["./launch.sh"]
