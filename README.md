# Wifidog Auth Flask

[![Build Status](http://drone.datashaman.com/api/badges/datashaman/wifidog-auth-flask/status.svg)](http://drone.datashaman.com/datashaman/wifidog-auth-flask)
[![Coverage Status](https://coveralls.io/repos/github/datashaman/wifidog-auth-flask/badge.svg?branch=master)](https://coveralls.io/github/datashaman/wifidog-auth-flask?branch=master)

Voucher authentication server for Wifidog Captive Portal written in Python Flask. WIP.

Set a time limit or transfer limit (in MB) before the voucher is invalidated. User accounts coming soon.

## Docker

Setup the following aliases to run the docker image. Put this in your _.bashrc_ or _.zshrc_:

    alias wifidog-server="docker run --env-file $HOME/.config/wifidog/env -p 5000:5000 -v auth-data:/var/app/data -v auth-uploads:/var/app/uploads -i -t datashaman/wifidog-auth-flask"
    alias wifidog="docker run --env-file $HOME/.config/wifidog/env -v auth-data:/var/app/data -v auth-uploads:/var/app/uploads --rm -it datashaman/wifidog-auth-flask"

Create the file at _$HOME/.config/wifidog/env_ to store your secrets. Look at _.env.example_ for inspiration. Don't add _SQLALCHEMY_DATABASE_URI_, that is handled inside the container.

Use _wifidog-server_ to run the HTTP server. Use _wifidog_ to run CLI commands.

That will run the latest build of the docker image, by default running the HTTP server on port 5000.

It will persist the data to a local volume named *auth-data*, and the uploads to a local volume named *auth-uploads*. Change it as you see fit.

Various commands are available to help you manage the service:

    * wifidog create_country
    * wifidog create_currency
    * wifidog create_voucher
    * wifidog create_network
    * wifidog create_gateway
    * wifidog create_user
    * wifidog create_roles
    * wifidog create_product
    * wifidog process_vouchers

Create roles:

    wifidog create_roles

Create a user with a role of _super-admin_:

    wifidog create_user user@example.com password super-admin

Create a network and gateway with that network:

    wifidog create_network example-network "Example Network"
    wifidog create_gateway example-network example-gateway "Example Gateway"

The Wifidog client software should point to this service with the correct *gw_id* to identify the gateway being served.

To run the HTTP server:

    wifidog-server

The command *process_vouchers* does the following:

    * Ends any vouchers with no time left.
    * Expires any new vouchers that are unused after a configurable age (default is _120_ minutes).
    * Archives any blocked, ended or expired vouchers that have not changed for a configurable age (default is _120_ minutes, the same config as above).

To run the command:

    wifidog process_vouchers

Put that (or the underlying `docker run` command) into a cron so the system keeps the vouchers list clean.

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
