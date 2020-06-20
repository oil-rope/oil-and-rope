# Oil &amp; Rope

[![Python](https://img.shields.io/badge/Python-3.7.6+-green.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-latest-blue.svg)](https://docs.docker.com/)
![Project Checker](https://github.com/oil-rope/oil-and-rope/workflows/Project%20Checker/badge.svg)
[![codecov](https://codecov.io/gh/oil-rope/oil-and-rope/branch/master/graph/badge.svg)](https://codecov.io/gh/oil-rope/oil-and-rope)

Oil &amp; Rope is a Python project for managing Roleplay Games.
The goald of this project is to make online roleplay easier and intuitive.

You can try now at our website [Oil & Rope Web](https://oilandrope-project.com/).

-   [The Project](#the-project)
-   [Installation](#installation)
-   [Docker](#docker)

## The Project

The main goal of *Oil &amp; Rope Project* is combine both real-time web interaction wit Discord Bots response.  
Since a lot of people often use Discord for roleplay gaming we thought it might be wonderful for everyone to enjoy a session either on Discord chat or Web (with its respective features).

The project is based on four fundamental technologies:

-   [Web with Django](#web)
-   [ASGI with Channels](#asgi)
-   [WebSocket components with React](#react-components)
-   [Discord Bot with Discord.py](#discord)

### Web

The entire web is based on Django Framework, [Django 3.0.x](https://docs.djangoproject.com/en/3.0/) to be specific.  
All views are tested CBV with Pytest (compatible with Unittest).

### ASGI

We use [django-channels](https://channels.readthedocs.io/) to deal with ASGI requests since we need real-time interaction with the user for sending and receiving information from Discord API.

### React Components

For dealing with real-time interaction in the frontend in an easy way we use React Components with native ES6 WebSockets.

### Discord

The web is directly linked to [Oil &amp; Rope Bot](https://discord.com/oauth2/authorize?client_id=474894488591007745&permissions=37604544&scope=bot), the bot that manages roleplay session that are currently open in [Oil &amp; Rope Web](https://oilandrope-project.com/).

## Installation

-   [Web](#setup-web)
-   [ASGI](#setup-channels)
-   [React](#setup-react)
-   [Discord](#setup-bot)

First of all we need to clone this repository `git clone https://github.com/oil-rope/oil-and-rope.git`.  
The dependencies are managed by [poetry](https://python-poetry.org/) and are easily installed by `poetry install`.  

> Note that this command will also create a *virtualenvironment*.  
> If you want to install dependencies via `requirements.txt` you can get this file running the following command `poetry export -f requirements.txt --dev --without-hashes -o requirements.txt`.

### Setup Web

> It's important to note that we have **two settings files**; `oilandrope/settings.py` and `oilandrope/dev_settings.py`.   
> `settings.py` it's intended to be used on production or with similar production environment since its features support for PostgreSQL Database, Mail and Hosts.  
> `dev_settings.py` it's supposed to *just work* by settings a **SECRET_KEY environment variable** (`export SECRET_KEY="here goes your key hash"`). It has support for local Redis, SQLite and debug tools such a [django-extensions](https://django-extensions.readthedocs.io/en/latest/) and [django-pdb](https://github.com/HassenPy/django-pdb).

> There're a couple of *environment variables* that might be helpful when developing or even deploying the app. A list of this variables can be found either in `.env.example` or `.envrc.example`.

1.  Run migrations: `python manage.py migrate --settings oilandrope.dev_settings`.
2.  *(Recommended) Run tests: `pytest`. Pytest it directly pointing to `dev_settings` in `setup.cfg`*
3.  Run server: `python manage.py runserver --settings oilandrope.dev_settings`.

### Setup Channels

We use Docker to simulate a Redis machine that manage ASGI requests.

1.  Run `docker run --rm -p 6739:6739 --name redis redis`. This docker machine will manage all ASGI requests if you are running the web with `dev_settings.py`.

### Setup React

For dealing with React Components we use [Node.js](https://nodejs.org/es/), [npm](https://www.npmjs.com/get-npm) and [webpack](https://www.npmjs.com/get-npm).  
There are two simple runs: `dev` for development and `build` for compiling production JS.

1.  Install dependencies: `npm install`.
2.  *(Recommended) Run tests: `npm run test`.*
3.  Compile JS: `npm run dev` for development (with watch) or `npm run build` for production.

JS bundles are stored in `frontend/static/frontend/dist/` and can be called by Django with `{% static %}`.

### Setup Bot

In order the bot to run you need some *environment variables* such as token and command.  
`BOT_TOKEN` is used to connect [discord.py](https://github.com/Rapptz/discord.py) to your bot via Discord bot's token.  
`BOT_COMMAND` is used as the command to call the bot.  

All extra environment variables can be found either in `.env.example` or `.envrc.example`.

1.  Run `python manage.py runbot --settings oilandrope.dev_settings`.

## Docker

You can setup a production-like environment with [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).  
The configuration file is `docker-compose.yml` and includes a PostgreSQL Database, ASGI machine with Daphne, WSGI machine with Gunicorn and Nginx.

1.  Run `docker-compose up`. This will run an nginx in your [localhost:8000](http://localhost:8000) internally pointing to 80.

> Alternative you can run `docker-compose up -d` to avoid having logs of every started machine in your output.