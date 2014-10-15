#!/usr/bin/env bash

if [ -z ${1} ] || [ "${1}" == "help" ]; then
    echo "Usage: delete-tokens.sh TOKEN_NAME [DATABASE_NAME]"
    echo "E.g.: delete-tokens.sh robin"
    echo "E.g.: delete-tokens.sh robin assets"
    exit 1
fi

DATABASE_NAME=assets

if [ -n "${2}" ]; then
    DATABASE_NAME=${2}
fi

mongo $DATABASE_NAME --eval "db.tokens.remove({'name': '$1'})"
