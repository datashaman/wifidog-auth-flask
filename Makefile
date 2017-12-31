PYTHON = python
REPO = datashaman/wifidog-auth-flask
BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
RELEASE = $(subst master,latest,$(BRANCH))
TAG = $(REPO):$(RELEASE)

tmuxp:
	tmuxp load .

serve:
	PORT=5000 python serve.py

sqlite3-development:
	sqlite3 instance/data/development.db

sqlite3-test:
	sqlite3 data/test.db

db-reset:
	rm -rf instance/data/development.db
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
	docker images | grep '<none>' | awk '{print $$3}' | xargs -r docker rmi

docker-prune: docker-prune-stopped docker-prune-untagged

browser-sync:
	browser-sync start --proxy http://127.0.0.1:5000 --files="auth/**"

lint:
	pylint auth

bootstrap: bootstrap-reference bootstrap-development

bootstrap-development: bootstrap-test
	cp data/test.db instance/data/development.db

bootstrap-reference:
	rm -rf data/reference.db
	FLASK_ENV=reference $(PYTHON) manage.py bootstrap_reference

bootstrap-test:
	rm -rf data/test.db
	FLASK_ENV=test $(PYTHON) manage.py bootstrap_test

watch:
	while inotifywait -e close_write -r ./auth/*.py ./auth/templates ./tests; do make test; done

test:
	FLASK_ENV=test $(PYTHON) -m unittest discover -s tests -f

coverage:
	FLASK_ENV=test coverage run --include='auth/*' -m unittest discover -s tests
	coveralls

setup:
	sudo -H apt-get install python-pip virtualenvwrapper libjpeg-dev libpng-dev libffi-dev
	sudo -H npm -g install gulp

development-install:
	pip install -r requirements/development.txt -r requirements/test.txt
	npm install
	gulp --dev

production-install:
	pip install -r requirements/production.txt
	npm install
	gulp

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	rm -rf auth/static/{fonts,scripts,styles}/* build/

graphs:
	$(PYTHON) auth/graphs.py

dot:
	dot -Tpng -O auth/graphs.dot && eog auth/graphs.dot.png

migrate: bootstrap-reference
	rm -f instance/data/new.db
	python manage.py migrate

packer-build:
	packer build packer.json
