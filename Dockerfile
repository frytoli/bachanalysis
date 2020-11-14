FROM python:3.9-slim

# Set bash to default shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Do not prompt apt for user input when installing packages
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && \
		apt install -y \
			build-essential \
			cmake \
			ffmpeg \
			libprotobuf-dev \
			libsm6 \
			libxext6 \
			protobuf-compiler \
			software-properties-common \
			wget && \
		apt dist-upgrade -y

ENV VIRTUAL_ENV=/venv
RUN python3.9 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install python packages
RUN pip install --no-dependencies \
	beautifulsoup4==4.9.3 \
	bs4==0.0.1 \
	certifi==2020.11.8 \
	chardet==3.0.4 \
	dlib==19.21.0 \
	html5lib==1.1 \
	idna==2.10 \
	lxml==4.6.1 \
	numpy==1.19.4 \
	opencv-python==4.4.0.46 \
	pandas==1.1.4 \
	python-dateutil==2.8.1 \
	pytz==2020.4 \
	requests==2.24.0 \
	six==1.15.0 \
	soupsieve==2.0.1 \
	urllib3==1.25.11 \
	webencodings==0.5.1

# Download and extract dlib face landmarks data file
RUN wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 && \
	bzip2 -dc shape_predictor_68_face_landmarks.dat.bz2 > /usr/bin/shape_predictor_68_face_landmarks.dat

# Set workdir
WORKDIR /home/

ENTRYPOINT ["python"]
