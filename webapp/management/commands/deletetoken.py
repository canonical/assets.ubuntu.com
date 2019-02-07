# Core packages
import sys

# Other packages
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "List authentication tokens"

    def add_arguments(self, parser):
        parser.add_argument(
            "token-name",
            type=str,
            help="The name for this token (e.g.: default)",
        )

    def handle(self, *args, **options):
        name = options["token-name"]

        deleted = settings.TOKEN_MANAGER.delete(name)

        if deleted:
            print("Deleted token '{}'".format(name), file=sys.stderr)
        else:
            print("Token '{}' not found".format(name), file=sys.stderr)
