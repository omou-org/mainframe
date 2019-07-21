SHELL := /bin/bash # Use bash syntax
GIT=git
PROJ=mainframe
PYTHON=python3
VENV_PATH=$$HOME/.virtualenvs/${PROJ}

all: help

.PHONY: setup
setup: cleandb clean-venv requirements startdb
	echo "Waiting for postgres to accept connections..."
	sleep 5
	source "$(VENV_PATH)/bin/activate"; \
	export DJANGO_ENV_MODULE=mainframe.settings.local; \
	./manage.py migrate
	echo "Now run 'workon $(PROJ)', and you're set!"

.PHONY: clean-venv
clean-venv:
	rm -rf $(VENV_PATH)
	$(PYTHON) -m venv $(VENV_PATH) --clear
	pip install --upgrade pip
	echo "export DJANGO_ENV_MODULE=mainframe.settings.local" >> $(VENV_PATH)/bin/postactivate
	echo "unset DJANGO_ENV_MODULE" >> $(VENV_PATH)/bin/postdeactivate

.PHONY: requirements
requirements:
	source "$(VENV_PATH)/bin/activate"; \
	for f in `ls requirements/` ; do pip install -r requirements/$$f ; done

.PHONY: clean-requirements
clean-requirements:
	pip freeze | xargs pip uninstall -y
	$(MAKE) requirements

.PHONY: startdb
startdb:
	docker-compose -p $(PROJ) -f docker/docker-compose.yml up -d --no-recreate

.PHONY: cleandb
cleandb:
	docker-compose -p $(PROJ) -f docker/docker-compose.yml down

.PHONY: stopdb
stopdb:
	docker-compose -p $(PROJ) -f docker/docker-compose.yml stop