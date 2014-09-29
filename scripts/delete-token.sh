#!/usr/bin/env bash

if [ -z ${1} ]; then
    echo "Usage: delete-tokens.sh NAME"
    echo "E.g.: delete-tokens.sh robin"
    exit 1
fi

mongo assets --eval "db.tokens.remove({'name': '$1'})"
