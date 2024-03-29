# Oil &amp; Rope

[![Python](https://img.shields.io/badge/Python-3.9.x,%203.10.x-green.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-latest-blue.svg)](https://docs.docker.com/)
![Project Checker](https://github.com/oil-rope/oil-and-rope/workflows/Project%20Checker/badge.svg)
[![codecov](https://codecov.io/gh/oil-rope/oil-and-rope/branch/develop/graph/badge.svg)](
https://codecov.io/gh/oil-rope/oil-and-rope)
[![discord server](https://dcbadge.vercel.app/api/server/exJTgPme?style=flat&theme=default-inverted)](
https://discord.gg/exJTgPme)

Oil &amp; Rope is a Python project for managing Roleplay Games.
The goal of this project is to make online roleplay easier and intuitive.

You can try now at our website [Oil & Rope Web](https://oilandrope-project.com/index/).

<!-- TOC -->
* [Oil &amp; Rope](#oil-amp-rope)
  * [The Project](#the-project)
    * [Web](#web)
    * [ASGI](#asgi)
    * [Discord](#discord)
  * [Quickstart](#quickstart)
    * [TL;DR;](#tldr)
  * [Installation](#installation)
    * [Setup Web](#setup-web)
    * [[Optional] Setup Channels](#optional-setup-channels)
    * [[Optional] Setup Bot](#optional-setup-bot)
<!-- TOC -->

## The Project

The main goal of *Oil &amp; Rope Project* is combine both real-time web interaction with Discord Bots response.  
Since a lot of people often use Discord for roleplay gaming we thought it might be wonderful for everyone to enjoy a
session either on Discord chat or Web (with its respective features).

The project is based on three fundamental technologies:

- [Web with `Django`](#web)
- [WebSockets with `django-channels`](#asgi)
- [Discord Bot with `discord.py`](#discord)

### Web

The entire web is based on [Django Framework](https://docs.djangoproject.com/en/4.0/).  
All views are tested CBV with Pytest (using base Django's [TestCase](
https://docs.djangoproject.com/en/4.0/topics/testing/overview/)).

### ASGI

We use [django-channels](https://channels.readthedocs.io/) to deal with ASGI requests
since we need real-time interaction with the user for sending and receiving information
from Discord API.  
This allows us to create [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) so the frontend
can communicate with the backend immediately.

### Discord

The web is directly linked to
[Oil &amp; Rope Bot](
https://discordapp.com/oauth2/authorize?client_id=474894488591007745&permissions=201337920&scope=bot),
the bot that manages roleplay session that are currently open in [Oil &amp; Rope Web](https://oilandrope-project.com/).  
This is achieved by the library [discord.py](https://discordpy.readthedocs.io/en/stable/) which is based on
[Discord Gateways](https://discord.com/developers/docs/topics/gateway).

## Quickstart

If you want to just run the project to see how it looks like you can use our development docker images

> These images **are not intended for production environments** and verbose error messages are gonna be displayed.

As part of out CI/CD we create images for every new feature we are adding  and once these branches have passed the
GitHub Actions' tests an image under the following naming rules `oilandrope/core:<feature-type>-<feature-ID>` for
example if a branch called `feature/OAR-44` (named after *OAR-44 - Character creation*) is pushed an image
`oilandrope/core:feature-OAR-44` will be created.  
This means you can just run a docker image under the name of `oilandrope/core:feature-OAR-44` and you'll have the latest
changes for that feature (if it isn't already implemented).

In order to create and access as admin user (Django's Superuser) you can set the environment variable `ADMIN_PASSWORD`
to create a user with username `admin` and given password.

### TL;DR;

1. Run `docker run -ti -p 8000:8000 -e ADMIN_PASSWORD=p4ssw0rd oilandrope/core:develop`
2. Access [localhost:8000](http://localhost:8000/accounts/auth/login/).
3. Set username `admin` and password `p4ssw0rd`.

## Installation

First of all we need to clone this repository `git clone https://github.com/oil-rope/oil-and-rope.git`.  
The dependencies are managed by [poetry](https://python-poetry.org/) and are easily installed by `poetry install`.  

> Note that this command will also create a *virtual environment*.  
> If you want to install dependencies via `requirements.txt` you can get this file running the following command
> `poetry export -f requirements.txt --dev --without-hashes -o requirements.txt`.

### Setup Web

> It's important to note that we have **two settings files**; `oilandrope/settings.py` and `oilandrope/dev_settings.py`.
>
> - `settings.py` it's intended to be used on production or with similar production environment since its features
support for PostgreSQL Database, Mail and Hosts.  
> - `dev_settings.py` it's supposed to *just work* by just setting environment variables.  
> It has support for local Redis, SQLite and debug tools such a [django-extensions](
https://django-extensions.readthedocs.io/en/latest/).

1. Set environment variables: `cp .env.example .env`
2. Set settings: Change `DJANGO_SETTINGS_MODULE` to `oilandrope.dev_settings`.
3. Run migrations: `python manage.py migrate`.
4. *(Recommended) Run tests: `python manage.py test`.*
5. Run server: `python manage.py runserver`.

### [Optional] Setup Channels

We use Docker to simulate a Redis machine that manage ASGI requests.

1. Run `docker run --rm -p 127.0.0.1:6379:6379 --name oar_redis --detach redis:6.2`.

> This docker machine will manage all ASGI requests if you are running the web with `dev_settings.py`.  
> This **does not work** with `runserver_plus`.

### [Optional] Setup Bot

In order the bot to run you need some *environment variables* such as token and command.  
`BOT_TOKEN` is used to connect [discord.py](https://github.com/Rapptz/discord.py) to your bot via Discord bot's token.  
`BOT_COMMAND` is used as the command to call the bot.  

1. Change `BOT_TOKEN` on `.env` with your token.
2. Change `BOT_COMMAND` on `.env` with a command to call the bot.
3. Run `python manage.py runbot`.
