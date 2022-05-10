from django.core.management import call_command
from django.core.management.base import BaseCommand

from ... import __title__


class Command(BaseCommand):
    help = "Preloads structures required for this app"

    def handle(self, *args, **options):
        # Load structures
        call_command(
            "eveuniverse_load_types",
            __title__,
            "--category_id_with_dogma",
            "65",
            "--group_id",
            "365",
            "--type_id",
            "2233",
            "--category_id",
            "66",
        )
