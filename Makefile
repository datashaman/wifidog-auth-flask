install:
	npm install
	npm prune
	bower install
	bower prune
	cd bower_components/purecss && npm install && node_modules/.bin/grunt
	gulp

.PHONY: install
