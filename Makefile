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
	bash bootstrap.sh

remove-db:
	rm data/local.db

reboot: remove-db bootstrap

clean:
	find . -name '*.pyc' -delete

.PHONY: serve install bootstrap clean remove-db reboot
