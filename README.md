# Oil &amp; Rope

[![Python](https://img.shields.io/badge/Python-3.7.6+-green.svg?style=flat-square)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-latest-blue.svg?style=flat-square)](https://docs.docker.com/)
[![Build Status for Develop](https://travis-ci.com/oil-rope/oil-and-rope.svg?branch=develop)](https://travis-ci.com/oil-rope/oil-and-rope)
[![codecov](https://codecov.io/gh/oil-rope/oil-and-rope/branch/master/graph/badge.svg)](https://codecov.io/gh/oil-rope/oil-and-rope)

Oil &amp; Rope is a Python project for managing Roleplay Games.

## Setup for linux

1. Clone the github repository

    `$ git clone https://github.com/oil-rope/oil-and-rope.git`

2. Install necessary tools

   - Anaconda (recommended)
   - Docker (needed)
   - npm (needed for developers)
   - nodejs (needed for developers)

3. Install the requirements

    - For developers:

        `$ pip install -r requirements/requirements_develop.txt`

    - For testers:

        `$ pip install -r requirements/requirements_base.txt`

4. For development and testing use `dev_settings.py`

5. Create and run a Docker Container for Redis (in order to use WebSockets)

    `$ docker run --rm -p 6739:6739 --name redis redis`

6. For React Views install npm dependencies

    `$ npm install`

7. Apply migrations

    `$ python manage.py migrate --settings oilandrope.dev_settings`

8. Run server pointing to the develop settings

    `$ python manage.py runserver --settings oilandrope.dev_settings`
