FROM debian:stable

# Updating container
RUN apt-get update

# Installing configuration stuff
RUN apt-get install --assume-yes pkg-config apt-utils
RUN apt-get install --assume-yes graphviz libgraphviz-dev
RUN apt-get install --assume-yes git
# Installing Python
RUN apt-get install --assume-yes python3 python3-pip locales locales-all gettext

# Activating UTF-8
RUN sed -i -e 's/# en_GB.UTF-8 UTF-8/en_GB.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG en_GB.UTF-8
ENV LANGUAGE en_GB
ENV LC_ALL en_GB.UTF-8

# Adding requirements.txt to temporal folder
ADD ./requirements.txt /tmp/requirements.txt

# Moving to TMP
WORKDIR /tmp/

# Updating pip and setuptools
RUN python3 -m pip install -U pip
RUN pip install -U setuptools

# Installing dependencies
RUN pip install -r requirements.txt

# Setting up Bash Completion
RUN echo "\n\nif [ -f /etc/bash_completion ]; then\n . /etc/bash_completion\nfi\n\n" >> /etc/profile

# Moving to web folder
WORKDIR /oilandrope/oilandrope/
