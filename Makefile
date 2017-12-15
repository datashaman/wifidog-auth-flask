PYTHON = python
REPO = datashaman/wifidog-auth-flask
BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
RELEASE = $(subst master,latest,$(BRANCH))
TAG = $(REPO):$(RELEASE)

tmuxp:
	tmuxp load .

serve:
	PORT=5000 python serve.py

serve-production:
	gunicorn --reload -b '127.0.0.1:5000' 'auth:create_app()'

sqlite3:
	sqlite3 data/local.db

sqlite3-tests:
	sqlite3 tests/tests.db

db-reset:
	rm -rf data/local.db
	python manage.py bootstrap_instance

build-static:
	npm install
	gulp

docker-prepare: clean

docker-build: docker-prepare
	./build.sh
	docker build -t $(TAG) .

docker-push:
	docker push $(TAG)

docker-run:
	docker run --env-file .env -p 5000:5000 -i -t $(TAG)

docker-run-persistent:
	docker run --env-file .env -p 5000:5000 -v auth-data:/var/app/data -i -t $(TAG)

docker-prune-stopped:
	docker ps -a -q | xargs -r docker rm

docker-prune-untagged:
	docker images | grep '^<none>' | awk '{print $$3}' | xargs -r docker rmi

docker-prune: docker-prune-stopped docker-prune-untagged

browser-sync:
	browser-sync start --proxy http://127.0.0.1:5000 --files="auth/**"

lint:
	pylint auth

bootstrap-local: bootstrap-tests
	cp tests/tests.db data/local.db

bootstrap-reference:
	rm -f data/local.db
	$(PYTHON) manage.py bootstrap_reference
	mv data/local.db data/reference.db

bootstrap-tests:
	rm -rf tests/tests.db && touch tests/tests.db
	TESTING=true $(PYTHON) manage.py bootstrap_tests

watch:
	while inotifywait -e close_write -r ./auth/*.py ./auth/templates ./tests; do make test; done

test:
	TESTING=true $(PYTHON) -m unittest discover -s tests -f

coverage:
	TESTING=true coverage run --include='auth/*' -m unittest discover -s tests
	coveralls

setup:
	sudo -H apt-get install python-pip virtualenvwrapper libjpeg-dev libpng-dev libffi-dev
	sudo -H npm -g install gulp

development-install:
	pip install -r requirements-tests.txt
	npm install
	gulp --dev

production-install:
	pip install -r requirements.txt
	npm install
	gulp

bootstrap:
	$(PYTHON) bootstrap.py

remove-db:
	rm -f local.db

reboot: remove-db bootstrap

clean:
	find . -name '*.pyc' -delete
	rm -rf auth/static/{fonts,scripts,styles}/* build/

graphs:
	$(PYTHON) auth/graphs.py

dot:
	dot -Tpng -O auth/graphs.dot && eog auth/graphs.dot.png

migrate: bootstrap-reference
	rm -f data/new.db
	python manage.py migrate
