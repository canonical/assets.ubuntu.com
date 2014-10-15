#!/usr/bin/env bash

if [ -z ${1} ] || [ "${1}" == "help" ]; then
    echo "Usage: create-random-token.sh TOKEN_NAME [DATABASE_NAME]"
    echo "E.g.: create-random-token.sh robin"
    echo "E.g.: create-random-token.sh robin assets"
    exit 1
fi

DATABASE_NAME=assets

if [ -n "${2}" ]; then
    DATABASE_NAME=${2}
fi

mongo $DATABASE_NAME --eval "db.tokens.insert({'token': '`uuidgen -r | sed 's/-//g'`', 'name': '$1'})"
mongo $DATABASE_NAME --eval "printjson(db.tokens.find({'name': '$1'}).toArray())"
