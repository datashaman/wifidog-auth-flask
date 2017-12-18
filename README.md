# Wifidog Auth Flask

[![Build Status](http://drone.datashaman.com/api/badges/datashaman/wifidog-auth-flask/status.svg)](http://drone.datashaman.com/datashaman/wifidog-auth-flask)
[![Coverage Status](https://coveralls.io/repos/github/datashaman/wifidog-auth-flask/badge.svg?branch=master)](https://coveralls.io/github/datashaman/wifidog-auth-flask?branch=master)

Voucher authentication server for Wifidog Captive Portal written in Python Flask. WIP.

Python 3.6 is the only version tested.

Set a time limit or transfer limit (in MB) before the voucher is invalidated. User accounts coming soon.

## Docker

Setup the following aliases to run the docker image. Put this in your _.bashrc_ or _.zshrc_:

    alias wifidog-server="docker run --env-file $HOME/.config/wifidog/.env -p 5000:5000 -v $HOME/.config/wifidog:/var/app/instance -it datashaman/wifidog-auth-flask"
    alias wifidog="docker run --env-file $HOME/.config/wifidog/.env -v $HOME/.config/wifidog:/var/app/instance --rm -it datashaman/wifidog-auth-flask"

Create the file at _$HOME/.config/wifidog/.env_, and it should contain the following entry:

    FLASK_ENV=production

Copy _instance.cfg.example_ and edit:

    cp instance.cfg.example $HOME/.config/wifidog/production.cfg

The instance config file must match the supplied *FLASK_ENV*.

Bootstrap the instance (giving the country ISO code and title to be used) and create a super-admin user.

    wifidog bootstrap_instance ZA "South Africa"
    wifidog create_user super-admin@example.com password super-admin

Run the server:

    wifidog-server

The database and uploads will be persisted in _$HOME/.config/wifidog_ folder.

NB: Use _wifidog-server_ to run the HTTP server. Use _wifidog_ to run CLI commands.

That will run the latest build of the docker image, by default running the HTTP server on port 5000.

Various commands are available to help you manage the service:

    * wifidog create_country
    * wifidog create_currency
    * wifidog create_gateway
    * wifidog create_network
    * wifidog create_product
    * wifidog create_roles
    * wifidog create_user
    * wifidog create_voucher
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

When you are not running via docker, use these commands directly as follows:

    python manage.py create_user ...

All the commands have help text, use __--help__.

## Development

Setup required (for Ubuntu or Debian):

    sudo -H apt-get install tzdata
    curl -L https://deb.nodesource.com/setup_8.x | bash -
    sudo -H apt-get install nodejs python3 python3-pip python3-setuptools virtualenvwrapper libjpeg-dev libpng-dev libffi-dev libxml2-dev libxslt-dev
    sudo -H npm install -g gulp

Logout and login to activate virtualenvwrapper then:

    mkvirtualenv auth -p /usr/bin/python3

Make sure you're in your projects folder and clone the repository:

    git clone https://github.com/datashaman/wifidog-auth-flask.git auth

Go into the folder and install the dependencies (you should be in your virtualenv at this point):

    cd auth
    setvirtualenvproject
    pip install -r requirements.txt
    npm install

Build the static files (see gulpfile.js for details):

	gulp

Create a _.env_ file:

    echo "FLASK_ENV=development" > .env

Create an instance settings file. Copy the example and edit to your taste:

    cp instance.cfg.example > instance/development.cfg

Sensitive config is kept in the instance settings file. It must match the supplied *FLASK_ENV* variable.

Please read the Makefile for many useful development shortcuts.
