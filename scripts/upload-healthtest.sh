#!/usr/bin/env bash

BASEDIR=$(dirname $0)

cd ${BASEDIR}
./upload-asset.py --url-path healthtest --server-url http://localhost:8080/v1/ data/healthtest

exit_code=$?

# If the file exists we'll get a 73 exit code
# In this case this isn't an error
if [ ${exit_code} -eq 73 ]; then
    exit 0
else
    exit ${exit_code}
fi
