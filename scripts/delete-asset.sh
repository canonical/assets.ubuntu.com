#!/usr/bin/env bash

# What's this directory?
BASEDIR=$(dirname $0)

# Where is the environment?
ENVPATH=${VIRTUAL_ENV}
if [ -z ${ENVPATH} ]; then ENVPATH=env; fi

vex --path ${ENVPATH} ${BASEDIR}/.delete-asset.py $@
