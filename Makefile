serve:
	python manage.py runserver -p 8080

serve-production:
	gunicorn --reload -b '127.0.0.1:8080' 'app:create_app()'

nodemon-tests:
	rm -f data/tests.db
	python manage.py bootstrap_tests
	nodemon tests.py

tests:
	rm -f data/tests.db
	python manage.py bootstrap_tests
	python tests.py

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
	rm -rf app/static/styles/*
	rm -rf app/static/scripts/*

graphs:
	python app/graphs.py

dot:
	dot -Tpng -O app/graphs.dot && eog app/graphs.dot.png

.PHONY: serve install bootstrap clean remove-db reboot
