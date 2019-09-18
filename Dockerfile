FROM ubuntu:18.04

RUN apt-get update -y

RUN apt-get install -y libsm6 # required by opencv
RUN apt-get install -y python3.5
RUN apt-get install -y python3-pip

RUN pip3 install opencv-python==3.4.0.12
RUN pip3 install requests==2.22.0

ADD . /app
