serve:
	gunicorn -k gevent -b '127.0.0.1:8080' 'app:create_app()'

setup:
	sudo apt-get install nodejs npm python-pip virtualenvwrapper libjpeg-dev libpng-dev libffi-dev
	sudo npm install -g bower gulp

install:
	pip install -r requirements.txt
	npm install
	npm prune
	bower install
	bower prune
	cd bower_components/pure && npm install && node_modules/.bin/grunt
	cd bower_components/zepto && npm install && MODULES="zepto ajax callbacks deferred event" npm run-script dist
	gulp

bootstrap:
	python bootstrap.py

remove-db:
	rm -f data/local.db

reboot: remove-db bootstrap

clean:
	find . -name '*.pyc' -delete

.PHONY: serve install bootstrap clean remove-db reboot
