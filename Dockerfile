FROM ubuntu:18.04

RUN apt-get update -y

RUN apt-get install -y ffmpeg
RUN apt-get install -y libsm6 # required by opencv
RUN apt-get install -y libxext6 # required by opencv
RUN apt-get install -y libxrender-dev # required by opencv
RUN apt-get install -y locales # required by mocha
RUN apt-get install -y python3.5
RUN apt-get install -y python3-pip

RUN pip3 install g2p-en==2.1.0
RUN pip3 install google-cloud-error-reporting==0.33.0
RUN pip3 install joblib==0.14.0
RUN pip3 install mock==4.0.2
RUN pip3 install opencv-python==3.4.0.12
RUN pip3 install pytest==3.2.1
RUN pip3 install pytest-mocha==0.1.0
RUN pip3 install pytest-only==1.2.2
RUN pip3 install pyyaml==5.1.2
RUN pip3 install requests==2.22.0
RUN pip3 install scipy==1.3.1
RUN pip3 install watchdog==0.8.3

RUN python3 -m nltk.downloader averaged_perceptron_tagger
RUN python3 -m nltk.downloader cmudict
RUN python3 -m nltk.downloader punkt

# Setup unicode support (required by mocha)
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install gcsfuse
RUN apt-get install -y curl
RUN apt-get install -y lsb-release

RUN export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s` && \
	echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | \
	tee /etc/apt/sources.list.d/gcsfuse.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

RUN apt-get update -y
RUN apt-get install -y gcsfuse

# Install gcloud
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
	tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

RUN apt-get install -y apt-transport-https
RUN apt-get install -y ca-certificates

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
	apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

RUN apt-get update -y
RUN apt-get install -y google-cloud-sdk

ADD . /app
