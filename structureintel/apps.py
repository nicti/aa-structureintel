from django.apps import AppConfig

from . import __version__


class StructureIntelConfig(AppConfig):
    name = "structureintel"
    label = "structureintel"
    verbose_name = f"Structures v{__version__}"
