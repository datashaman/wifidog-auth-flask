Wifidog Auth Flask
==================

Time-based voucher authentication server for Wifidog Captive Portal written in Python Flask. WIP.

Bandwidth-based vouchering coming soon.

Setup required (for Ubuntu or Debian):

    sudo apt-get install nodejs npm python-pip virtualenvwrapper libjpeg-dev libpng-dev libffi-dev libxml2-dev libxslt-dev redis-server
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
	cd node_modules/purecss && npm install && node_modules/.bin/grunt
	cd node_modules/zepto && npm install && MODULES="zepto ajax callbacks deferred event" npm run-script dist

Build the static files (see gulpfile.js for details):

	gulp

Copy the sample .env file to its correct place (and edit it to suit your needs):

    cp .env.example .env

Sensitive config is kept in the .env file, non-sensitive config is in config.py.

Bootstrap the database (stored at data/local.db):

    python manage.py create_roles

    python manage.py create_network example-network "Example Network"
    python manage.py create_gateway example-network example-gateway "Example Gateway"

    python manage.py create_user -e super@example.com -p password -r super-admin
    python manage.py create_user -e network@example.com -p password -r network-admin -n example-network
    python manage.py create_user -e gateway@example.com -p password -r gateway-admin -n example-network -g example-gateway

Read the help for each command for more options. Read the Makefile for other development tasks.
