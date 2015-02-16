#!/usr/bin/env bash

set -e

if [ -z ${1} ] || [ "${1}" == "help" ]; then
    echo "Usage: delete-tokens.sh TOKEN_NAME"
    echo "E.g.: delete-tokens.sh robin"
    exit 1
fi

TOKEN_NAME=${1}
DB_RUN="mongo assets --quiet --eval"

if [[ $(${DB_RUN} "db.tokens.find({'name': '${TOKEN_NAME}'}).size()") -ne '0' ]]; then
	${DB_RUN} "db.tokens.remove({'name': '${TOKEN_NAME}'})"
	echo "Token '${TOKEN_NAME}' deleted"
else
	echo "Token '${TOKEN_NAME}' not found"
	exit 1
fi
