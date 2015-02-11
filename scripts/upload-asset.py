#!/usr/bin/env python

# System packages
import argparse
import os

# Modules
from swiftclient.client import Connection as SwiftConnection

# Import app code
from script_helpers import add_app_dir_to_path
add_app_dir_to_path()
import settings
from mappers import FileManager, DataManager

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

# Managers
# ===
data_manager = DataManager(data_collection=settings.MONGO_DB['asset_data'])
file_manager = FileManager(
    SwiftConnection(
        os.environ.get('OS_AUTH_URL'),
        os.environ.get('OS_USERNAME'),
        os.environ.get('OS_PASSWORD'),
        auth_version='2.0',
        os_options={'tenant_name': os.environ.get('OS_TENANT_NAME')}
    )
)

with open(file_path) as upload_file:
    file_data = upload_file.read()

    if not url_path:
        url_path = file_manager.generate_asset_path(
            file_data,
            friendly_name
        )

    # Create file
    file_manager.create(file_data, url_path)

    # Once the file is created, create file metadata
    data_manager.update(url_path, tags)

print data_manager.fetch_one(url_path)
