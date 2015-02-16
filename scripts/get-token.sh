#!/usr/bin/env bash

set -e

if [ -z ${1} ] || [ "${1}" == "help" ]; then
    echo "Usage: get-token.sh TOKEN_NAME"
    echo "e.g.: get-token.sh robin"
    exit 1
fi

TOKEN_NAME=${1}
DB_RUN="mongo assets --quiet --eval"

if [[ $(${DB_RUN} "db.tokens.find({'name': '${TOKEN_NAME}'}).size()") -ne '0' ]]; then
    TOKEN=$(${DB_RUN} "db.tokens.find({'name': '${TOKEN_NAME}'})[0].token")
    echo "Existing '${TOKEN_NAME}' token: ${TOKEN}"
else
    TOKEN=`uuidgen -r | sed 's/-//g'`
    ${DB_RUN} "db.tokens.insert({'token': '${TOKEN}', 'name': '${TOKEN_NAME}'})"
    echo "Token '${TOKEN_NAME}' created: ${TOKEN}"
fi
