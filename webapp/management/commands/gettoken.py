# Core packages
import sys

# Other packages
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'List authentication tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            'token-name',
            type=str,
            help='The name for this token (e.g.: default)'
        )

    def handle(self, *args, **options):
        name = options['token-name']

        token = settings.TOKEN_MANAGER.create(name)

        if token:
            print("Created token '{}'".format(name), file=sys.stderr)
        else:
            token = settings.TOKEN_MANAGER.fetch(name)
            print("Found Token '{}'".format(name), file=sys.stderr)

        print(token['token'])
