serve:
	python app.py

install:
	npm install
	npm prune
	bower install
	bower prune
	cd bower_components/purecss && npm install && node_modules/.bin/grunt
	cd bower_components/zepto && npm install && MODULES="zepto ajax callbacks deferred event" npm run-script dist
	gulp

bootstrap:
	python manage.py seed_roles
	python manage.py seed_networks
	python manage.py create_user -e sa@example.com -p admin -r super-admin
	python manage.py create_user -e na@example.com -p admin -r network-admin -n test
	python manage.py create_user -e ga@example.com -p admin -r gateway-admin -n test -g test

clean:
	find . -name '*.pyc' -delete

.PHONY: serve install bootstrap clean
