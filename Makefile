serve:
	python manage.py runserver -p 8080

serve-production:
	gunicorn --reload -b '127.0.0.1:8080' 'app:create_app()'

browser-sync:
	browser-sync start --proxy http://127.0.0.1:8080 --files="app/**"

nodemon-tests: bootstrap-tests
	nodemon tests.py

bootstrap-tests:
	rm -f tests.db
	python manage.py bootstrap_tests

tests:
	python tests/test_unit.py

tests-webdriver:
	python tests/test_webdriver.py

setup:
	sudo apt-get install python-pip virtualenvwrapper libjpeg-dev libpng-dev libffi-dev
	sudo npm install -g bower gulp

development-install:
	bundle install
	pip install -r requirements.txt
	npm install
	npm prune
	bower install
	bower prune
	cd bower_components/pure && npm install && node_modules/.bin/grunt
	cd bower_components/zepto && npm install && MODULES="zepto ajax callbacks deferred event" npm run-script dist
	gulp --dev

production-install:
	bundle install --without development --deployment --jobs=3 --retry=3
	pip install -r requirements.txt
	npm install
	npm prune
	bower install
	bower prune
	cd bower_components/pure && npm install && node_modules/.bin/grunt
	cd bower_components/zepto && npm install && MODULES="zepto ajax callbacks deferred event" npm run-script dist
	gulp

db-migrate:
	python manage.py db migrate

db-upgrade:
	python manage.py db upgrade

bootstrap:
	python bootstrap.py

remove-db:
	rm -f local.db

reboot: remove-db bootstrap

clean:
	find . -name '*.pyc' -delete
	rm -rf app/static/*

graphs:
	python app/graphs.py

dot:
	dot -Tpng -O app/graphs.dot && eog app/graphs.dot.png

deploy:
	fab -H ubuntu@auth.datashaman.com deploy

.PHONY: serve bootstrap clean remove-db reboot deploy tests
