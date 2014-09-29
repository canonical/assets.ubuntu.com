#!/usr/bin/env bash

if [ -z ${1} ]; then
    echo "Usage: create-random-token.sh NAME"
    echo "E.g.: create-random-token.sh robin"
    exit 1
fi

mongo assets --eval "db.tokens.insert({'token': '`uuidgen -r | sed 's/-//g'`', 'name': '$1'})"
mongo assets --eval "printjson(db.tokens.find({'name': '$1'}).toArray())"
