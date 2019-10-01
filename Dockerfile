FROM ubuntu:18.04

RUN apt-get update -y

RUN apt-get install -y curl # required by gcsfuse
RUN apt-get install -y libsm6 # required by opencv
RUN apt-get install -y libxext6 # required by opencv
RUN apt-get install -y libxrender-dev # required by opencv
RUN apt-get install -y lsb-release # required by gcsfuse
RUN apt-get install -y python3.5
RUN apt-get install -y python3-pip

RUN pip3 install opencv-python==3.4.0.12
RUN pip3 install requests==2.22.0
RUN pip3 install scipy==1.3.1

ADD . /app
RUN mkdir /data

# Install GCSFUSE
RUN export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s` && \
	echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | \
	tee /etc/apt/sources.list.d/gcsfuse.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

RUN apt-get update -y
RUN apt-get install -y gcsfuse
