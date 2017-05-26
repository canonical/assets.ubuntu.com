from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'List authentication tokens'

    def handle(self, *args, **options):
        all_tokens = settings.TOKEN_MANAGER.all()

        if not all_tokens:
            print("No tokens")
        else:
            print("Tokens\n===")
            for token in all_tokens:
                print("{name}: {token}".format(**token))
