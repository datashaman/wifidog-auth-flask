# Wifidog Auth Flask

[![Build Status](http://drone.datashaman.com/api/badges/datashaman/widog-auth-flask/status.svg)](http://drone.datashaman.com/api/badges/datashaman/wifidog-auth-flask/status.svg)
[![Coverage Status](https://coveralls.io/repos/github/datashaman/wifidog-auth-flask/badge.svg?branch=master)](https://coveralls.io/github/datashaman/wifidog-auth-flask?branch=master)

Time-based voucher authentication server for Wifidog Captive Portal written in Python Flask. WIP.

Bandwidth-based vouchering coming soon.

## Docker

Setup an alias to run the docker image. Put this in your _.bashrc_ or _.zshrc_:

    alias wifidog='docker run --env-file .env -p 5000:5000 -v auth-data:/var/app/data -i -t datashaman/wifidog-auth-flask'

That will run the latest build of the docker image, by default running the HTTP server on port 5000. It will persist the data to a local named volume called *auth-data*. Change it as you see fit.

Various other commands are available to help you manage the service:

    create_country
    create_currency
    create_voucher
    create_network
    create_gateway
    create_user
    create_roles
    create_product
    process_vouchers
    runserver

Create a user with a role of _super-admin_:

    wifidog create_user user@example.com password super-admin

Create a network and gateway with that network:

    wifidog create_network example-network "Example Network"
    wifidog create_gateway example-network example-gateway "Example Gateway"

The Wifidog client software should point to this service with the correct *gw_id* to identify the gateway being served.

To run the HTTP server:

    wifidog

Or:

    wifidog runserver

All the commands have help text, use __--help__.

## Development

Setup required (for Ubuntu or Debian):

    sudo apt-get install nodejs npm python-pip virtualenvwrapper libjpeg-dev libpng-dev libffi-dev libxml2-dev libxslt-dev
    sudo npm install -g gulp

Logout and login to activate virtualenvwrapper then:

    mkvirtualenv auth

Make sure you're in your projects folder and clone the repository:

    git clone https://github.com/datashaman/wifidog-auth-flask.git auth

Go into the folder and install the dependencies (you should be in your virtualenv at this point):

    cd auth
    setvirtualenvproject
    pip install -r requirements.txt
    npm install

Build the static files (see gulpfile.js for details):

	gulp

Copy the sample .env file to its correct place (and edit it to suit your needs):

    cp .env.example .env

Sensitive config is kept in the .env file, non-sensitive config is in config.py.

Please read the Makefile for many useful development shortcuts.
