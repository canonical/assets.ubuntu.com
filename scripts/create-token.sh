#!/usr/bin/env bash

if [ -z ${2} ] || [ "${1}" == "help" ]; then
    echo "Usage: create-token.sh TOKEN TOKEN_NAME [DATABASE_NAME]"
    echo "e.g.: create-token.sh 78347a5722964631b1efb862c116e30c robin"
    echo "e.g.: create-token.sh 78347a5722964631b1efb862c116e30c robin assets"
    exit 1
fi

DATABASE_NAME=assets

if [ -n "${3}" ]; then
    DATABASE_NAME=${3}
fi

mongo $DATABASE_NAME --eval "db.tokens.insert({'token': '$1', 'name': '$2'})"
mongo $DATABASE_NAME --eval "printjson(db.tokens.find({'name': '$2'}).toArray())"
