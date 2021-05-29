FROM python:3.8

# Update packages
RUN apt-get update
# Install dependencies
RUN apt-get install -y git vim nginx
RUN pip install pipenv

# Clone repository
RUN git clone https://gitlab.com/litecord/litecord.git /srv/litecord/

# Changing working dir to repository
WORKDIR /srv/litecord/

# Install dependencies
RUN pipenv install --dev

EXPOSE 80
EXPOSE 5001

# Start Nginx and Hypercorn
CMD /usr/sbin/service nginx start && /usr/bin/env pipenv run ./manage.py migrate && /usr/bin/env pipenv run hypercorn run:app
