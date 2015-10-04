install:
	npm install
	npm prune
	bower install
	bower prune
	cd bower_components/purecss && npm install && node_modules/.bin/grunt
	gulp

bootstrap:
	python manage.py seed_roles
	python manage.py create_admin -e admin@example.com -p admin

clean:
	find . -name '*.pyc' -delete

.PHONY: install bootstrap clean
