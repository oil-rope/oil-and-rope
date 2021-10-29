FROM python:3.9.5-slim

# Updating APT for installing pre-requisites
RUN apt update
# Installing C libraries for Postgres
RUN apt install -y gcc
RUN apt install -y libpq-dev

# Updating PIP
RUN python3 -m pip install -U pip
# Installing poetry
RUN python3 -m pip install poetry

# Copying sources
COPY . /app/
WORKDIR /app/

# Installing dependencies
RUN poetry install

# Copying entrypoint.sh
COPY ./compose/oilandrope/entrypoint.sh /bin/entrypoint.sh
ENTRYPOINT /bin/entrypoint.sh
