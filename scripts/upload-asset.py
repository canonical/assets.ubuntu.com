#!/usr/bin/env python

# System packages
import argparse
import errno
import sys
import os

# Import app code
from script_helpers import add_app_dir_to_path
add_app_dir_to_path()
from lib.file_helpers import create_asset

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "settings"
)
from django.conf import settings

# Get arguments
# ===
parser = argparse.ArgumentParser(
    description='Upload a file to an assets server.'
)
parser.add_argument(
    'file-path',
    help='The path to the file to upload'
)
parser.add_argument(
    '--url-path',
    help='The URL path to upload the file to'
)
parser.add_argument(
    '--tags',
    help='Tags to add to the uploaded file',
    default=''
)
parser.add_argument(
    '--server-url',
    help='The URL of the server',
    default='http://localhost:8080/v1/'
)

cmd_args = vars(parser.parse_args())

file_path = cmd_args['file-path']
url_path = cmd_args['url_path']
tags = cmd_args['tags']
server_url = cmd_args['server_url']

with open(file_path) as upload_file:
    try:
        url_path = create_asset(
            file_data=upload_file.read(),
            friendly_name=os.path.basename(upload_file.name),
            tags=tags,
            url_path=url_path
        )
    except IOError, create_error:
        if create_error.errno == errno.EEXIST:
            print "Error: Asset already exists at {0}".format(url_path)

            sys.exit(73)
        else:
            raise create_error


print settings.DATA_MANAGER.fetch_one(url_path)
