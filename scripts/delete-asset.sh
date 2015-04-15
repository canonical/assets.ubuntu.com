#!/usr/bin/env bash

# What's this directory?
BASEDIR=$(dirname $0)

# Where is the environment?
ENVPATH=${VIRTUAL_ENV}

if [ -z ${ENVPATH} ]; then ENVPATH=env; fi

if [ ! -d "${ENVPATH}" ]; then
    echo "Can't find environment. Do you need to run 'make setup'?"
    exit 1
fi

vex --path ${ENVPATH} ${BASEDIR}/.delete-asset.py $@
