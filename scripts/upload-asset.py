#!/usr/bin/env python

# System packages
import argparse

# Modules
from ubuntudesign import AssetMapper

# Import app code
from script_helpers import add_app_dir_to_path
add_app_dir_to_path()
from lib.db_helpers import auth_token


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
    '--server-url',
    help='The URL of the server',
    default='http://localhost:8080/v1/'
)

cmd_args = vars(parser.parse_args())

file_path = cmd_args['file-path']
url_path = cmd_args['url_path']
server_url = cmd_args['server_url']

asset_mapper = AssetMapper(
    server_url=server_url,
    auth_token=auth_token()
)
with open(file_path) as upload_file:
    if url_path:
        response = asset_mapper.create_at_path(
            asset_content=upload_file.read(),
            url_path=url_path
        )
    else:
        response = asset_mapper.create(
            asset_content=upload_file.read(),
            friendly_name=upload_file.name
        )

print response
