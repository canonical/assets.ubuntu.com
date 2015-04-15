#!/usr/bin/env python

# System packages
import argparse
import os

# Import app code
from script_helpers import add_app_dir_to_path
add_app_dir_to_path()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "settings"
)
from django.conf import settings

# Get arguments
# ===
parser = argparse.ArgumentParser(
    description='Delete a file from an assets server.'
)
parser.add_argument(
    'asset-path',
    help='The path to the file to upload'
)

cmd_args = vars(parser.parse_args())

asset_path = cmd_args['asset-path']

if (
    settings.FILE_MANAGER.delete(asset_path) and
    settings.DATA_MANAGER.delete(asset_path)
):
    print "Asset {0} deleted".format(asset_path)
else:
    print "Asset {0} not deleted. does it exists?".format(asset_path)
