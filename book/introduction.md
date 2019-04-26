# Introduction

## What is it?

This is yet another home automation that I'm building for myself as an open-source project.

## Features and goals

- As less configuration and customization as possible. It should just work without my close attention.
- Automation is a normal Python module, you can code whatever you want.
- Able to run on Raspberry Pi Zero (W).
- Does not require a custom OS image to be flashed onto SD-card. The Docker image should just work on any normal OS distribution.
- As less JavaScript as possible to speed up development.
- Custom devices built with [ESPHome](https://esphome.io/) should be supported.

## Technology stack

- Python 3.x: backend
- [AIOHTTP](https://aiohttp.readthedocs.io/): HTTP server and client
- [Bulma](https://bulma.io/): frontend
- [Jinja2](http://jinja.pocoo.org/): template engine
- [Nginx](https://nginx.org/): reverse-proxy for authentication and HTTPS support
- [Docker](https://www.docker.com/): for production deployment
