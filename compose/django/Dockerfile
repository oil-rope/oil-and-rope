FROM python:3.9.5

WORKDIR /tmp/

# Update packages
RUN apt-get update
# Install dependencies
RUN apt-get install -y gettext locales vim

# Copy and install requirements
COPY ./pyproject.toml /tmp/pyproject.toml
COPY ./poetry.lock /tmp/poetry.lock
RUN pip install poetry
RUN poetry export --dev -f requirements.txt -o /tmp/requirements.txt --without-hashes
RUN pip install -r /tmp/requirements.txt

# Set up locales
RUN dpkg-reconfigure locales
RUN echo "en_GB.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "es_ES.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "en_GB.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "en_GB UTF-8" >> /etc/locale.gen
RUN /usr/sbin/locale-gen

EXPOSE 8000

RUN echo "#!/bin/bash\npytest -sx" > /run_test_fail_fast && chmod 774 /run_test_fail_fast && ln /run_test_fail_fast /bin/run_test_fail_fast
RUN echo "#!/bin/bash\npytest -s" > /run_test && chmod 774 /run_test && ln /run_test /bin/run_test

WORKDIR /app/
