#!/usr/bin/env bash

BASEDIR=$(dirname $0)

cd ${BASEDIR}
./upload-asset.py --url-path healthtest --server-url http://localhost:8080/v1/ data/healthtest
