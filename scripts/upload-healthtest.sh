#!/usr/bin/env bash

BASEDIR=$(dirname $0)

cd ${BASEDIR}
./upload-asset.py --url-path ccotp/chinacachehealthtest.txt data/chinacachehealthtest.txt
