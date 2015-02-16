SHELL := /bin/bash # Use bash syntax

define HELP_TEXT
Ubuntu http assets server
===

Usage:

> make setup        # Prepare dependencies
> make develop      # Run the dev server

endef

ENVPATH=${VIRTUAL_ENV}
VEX=vex --path ${ENVPATH}

ifeq ($(ENVPATH),)
	ENVPATH=env
endif

ifeq ($(PORT),)
	PORT=8012
endif

.PHONY: pip-cache

##
# Print help text
##
help:
	$(info ${HELP_TEXT})

##
# Prepare the project
##
setup:
	# Install missing dependencies
	if ! dpkg -s mongodb libjpeg-dev zlib1g-dev libpng12-dev libmagickwand-dev python-dev &> /dev/null; then \
		sudo apt update && sudo apt install -y mongodb libjpeg-dev zlib1g-dev libpng12-dev libmagickwand-dev python-dev; \
	fi

	# Create virtual env folder, if not already in one
	-[ -z ${VIRTUAL_ENV} ] && virtualenv ${ENVPATH}

	# Install vex
	type ${VEX} &> /dev/null || pip install vex

	# Install requirements into virtual env
	${VEX} pip install -r requirements/dev.txt

develop:
	${VEX} python manage.py runserver_plus 0.0.0.0:${PORT}


rebuild-dependencies-cache:
	rm -rf pip-cache
	bzr branch lp:~webteam-backend/assets-server/dependencies pip-cache
	pip install --exists-action=w --download pip-cache/ -r requirements/standard.txt
	bzr commit pip-cache/ --unchanged -m 'automatically updated partners requirements'
	bzr push --directory pip-cache lp:~webteam-backend/assets-server/dependencies
	rm -rf pip-cache src
