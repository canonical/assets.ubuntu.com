import os
import sys


def add_app_dir_to_path():
    """
    Add assets server application directory
    to PYTHONPATH
    """
    file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(file_path)
    parent_directory = os.path.dirname(current_directory)
    app_directory = os.path.join(parent_directory, 'assets_server')
    sys.path.insert(1, app_directory)
