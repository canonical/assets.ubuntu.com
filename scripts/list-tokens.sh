#!/usr/bin/env bash

if [ "${1}" == "help" ]; then
    echo "Usage: list-tokens.sh [DATABASE_NAME]"
    echo "E.g.: list-tokens.sh"
    echo "E.g.: list-tokens.sh assets"
    exit 1
fi

DATABASE_NAME=assets

if [ -n "${1}" ]; then
    DATABASE_NAME=${1}
fi

mongo ${DATABASE_NAME} --eval "printjson(db.tokens.find().toArray())"
