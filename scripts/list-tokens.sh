#!/usr/bin/env bash

mongo assets --eval "printjson(db.tokens.find().toArray())"
