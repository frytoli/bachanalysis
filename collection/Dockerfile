FROM debian:stretch

# Set bash to default shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Do not prompt apt for user input when installing packages
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && \
		apt install -y software-properties-common && \
		apt dist-upgrade -y

RUN apt install -y \
		vim \
		strace \
		python3 \
		python3-pip \
		python3-setuptools \
		sudo \
		net-tools \
		build-essential

RUN	pip3 install virtualenv

# Add system user
RUN useradd -m -s /bin/bash user && \
		su user -c 'virtualenv -p python3 /home/user/venv'

# Add code and ensure ownership to the user
ADD main.py /home/user/main.py
ADD requirements.txt /home/user/requirements.txt
ADD src/scrapers/* /home/user/scrapers/
RUN chmod -R 744 /home/user

# Install python packages
RUN su user -c 'source /home/user/venv/bin/activate && pip3 install -r /home/user/requirements.txt'

# Run
ENTRYPOINT ["sh", "-c", ". /home/user/venv/bin/activate && ./home/user/main.py"]
