FROM debian:latest

# Updating container
RUN apt-get update

# Installing Python
RUN apt-get install --assume-yes python3 python3-pip locales locales-all gettext git

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

# Moving to web folder
WORKDIR /oilandrope/oilandrope/
