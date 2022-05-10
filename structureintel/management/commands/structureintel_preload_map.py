from django.core.management.base import BaseCommand
from eveuniverse.tasks import load_map


class Command(BaseCommand):
    help = "Preloads map for this app"

    def handle(self, *args, **options):

        # Load systems
        load_map()
