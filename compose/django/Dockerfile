FROM python:3.7

WORKDIR /tmp/

# Update packages
RUN apt-get update
# Install dependencies
RUN apt-get install -y gettext locales vim ruby-sass

# Copy and install requirements
COPY ./pyproject.toml /tmp/pyproject.toml
COPY ./poetry.lock /tmp/poetry.lock
RUN pip install poetry
RUN poetry export -f requirements.txt -o /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Installing Node and NPM
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs

# Set up locales
RUN dpkg-reconfigure locales
RUN echo "en_GB.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "es_ES.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "en_GB.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "en_GB UTF-8" >> /etc/locale.gen
RUN /usr/sbin/locale-gen

# Bash completation
RUN apt-get install -y bash-completion --no-install-recommends
RUN printf '\nif [ -f /etc/bash_completion ]; then\n\
  . /etc/bash_completion\n\
fi\n' >> /etc/profile