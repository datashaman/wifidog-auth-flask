serve:
	python app.py

install:
	pip install -r requirements.txt
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
	python manage.py create_user -e marlinf@datashaman.com -p marlinf -r super-admin
	python manage.py create_user -e info@thedrawingroomcafe.co.za -p admin -r gateway-admin -n datashaman -g tdr

clean:
	find . -name '*.pyc' -delete

.PHONY: serve install bootstrap clean
