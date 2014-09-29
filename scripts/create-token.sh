#!/usr/bin/env bash

if [ -z ${1} ] || [ -z ${2} ]; then
    echo "Usage: create-token.sh TOKEN NAME"
    echo "e.g.: create-token.sh 78347a5722964631b1efb862c116e30c robin"
    exit 1
fi

mongo assets --eval "db.tokens.insert({'token': '$1', 'name': '$2'})"
mongo assets --eval "printjson(db.tokens.find({'name': '$1'}).toArray())"
