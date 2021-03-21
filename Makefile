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

.PHONY: virtualenv
virtualenv:
	pip3 install virtualenv
	pip3 install virtualenvwrapper
	mkdir -p ~/.virtualenvs
	echo "export WORKON_HOME=~/.virtualenvs" >> ~/.bash_profile
	echo "export VIRTUALENVWRAPPER_SCRIPT=`which virtualenvwrapper.sh`" >> ~/.bash_profile
	echo "export VIRTUALENVWRAPPER_PYTHON=`which $(PYTHON)`" >> ~/.bash_profile
	echo "source `which virtualenvwrapper.sh`" >> ~/.bash_profile
	source ~/.bash_profile

.PHONY: clean-venv
clean-venv:
	rm -rf $(VENV_PATH)
	$(PYTHON) -m venv $(VENV_PATH) --clear
	export DJANGO_ENV_MODULE=mainframe.settings.local
	echo "export DJANGO_ENV_MODULE=mainframe.settings.local" >> $(VENV_PATH)/bin/postactivate
	echo "unset DJANGO_ENV_MODULE" >> $(VENV_PATH)/bin/postdeactivate

.PHONY: requirements
requirements:
	source "$(VENV_PATH)/bin/activate"; \
	pip install -r requirements.txt

.PHONY: clean-requirements
clean-requirements:
	pip freeze | xargs pip uninstall -y
	$(MAKE) requirements

.PHONY: startdb
startdb:
	docker-compose -p $(PROJ) -f docker/docker-compose.yml up -d --no-recreate
	$(PYTHON) manage.py migrate

.PHONY: cleandb
cleandb:
	docker-compose -p $(PROJ) -f docker/docker-compose.yml down

.PHONY: stopdb
stopdb:
	docker-compose -p $(PROJ) -f docker/docker-compose.yml stop

.PHONY: loaddb
loaddb:
	python manage.py migrate_summit_accounts
	python manage.py migrate_summit_courses
	python manage.py migrate_summit_enrollments
	python manage.py migrate_summit_tutoring
	python manage.py migrate_summit_tutoring_enrollments

.PHONY: cronjobs
cronjobs:
	python manage.py crontab add
