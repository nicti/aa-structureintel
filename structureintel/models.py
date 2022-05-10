from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveSolarSystem, EveType


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            ("delete_structure", "Can delete structure"),
        )


class Structure(models.Model):
    class State(models.IntegerChoices):
        """State of a structure"""

        # states Upwell structures
        ANCHOR_VULNERABLE = 1, _("anchor vulnerable")
        ANCHORING = 2, _("anchoring")
        ARMOR_REINFORCE = 3, _("armor reinforce")
        ARMOR_VULNERABLE = 4, _("armor vulnerable")
        DEPLOY_VULNERABLE = 5, _("deploy vulnerable")
        FITTING_INVULNERABLE = 6, _("fitting invulnerable")
        HULL_REINFORCE = 7, _("hull reinforce")
        HULL_VULNERABLE = 8, _("hull vulnerable")
        ONLINE_DEPRECATED = 9, _("online deprecated")
        ONLINING_VULNERABLE = 10, _("onlining vulnerable")
        SHIELD_VULNERABLE = 11, _("shield vulnerable")
        UNANCHORED = 12, _("unanchored")
        # starbases
        POS_OFFLINE = 21, _("offline")
        POS_ONLINE = 22, _("online")
        POS_ONLINING = 23, _("onlining")
        POS_REINFORCED = 24, _("reinforced")
        POS_UNANCHORING = 25, _("unanchoring ")
        # other
        NA = 0, _("N/A")
        UNKNOWN = 13, _("unknown")

    class PowerMode(models.TextChoices):
        FULL_POWER = "FU", _("Full Power")
        LOW_POWER = "LO", _("Low Power")
        ABANDONED = "AB", _("Abandoned")
        LOW_ABANDONED = "LA", _("Abandoned?")
        UNKNOWN = "UN", _("Unknown")

    power_mode = models.CharField(
        choices=PowerMode.choices, max_length=2, help_text="Power mode of the structure"
    )

    eve_solar_system = models.ForeignKey(EveSolarSystem, on_delete=models.CASCADE)
    eve_type = models.ForeignKey(
        EveType, on_delete=models.CASCADE, help_text="type of the structure"
    )
    last_updated_at = models.DateTimeField(
        null=True,
        default=None,
        blank=True,
        help_text="date this structure was last updated from the EVE server",
    )
    name = models.CharField(max_length=255, help_text="The full name of the structure")
    owner = models.CharField(max_length=255, help_text="The owner of the structure")
    reinforce_hour = models.PositiveIntegerField(
        validators=[MaxValueValidator(23)],
        null=True,
        default=None,
        blank=True,
        help_text=("Default reinforcement hour of this structure"),
    )

    def __str__(self) -> str:
        try:
            location_name = self.eve_solar_system.name
        except AttributeError:
            location_name = "?"
        return f"{location_name} - {self.name}"

    def get_absolute_url(self) -> str:
        return reverse("structureintel:index")


class StructureModule(models.Model):
    class Slot(models.TextChoices):
        HIGHSLOT = "Highslot"
        MEDSLOT = "Midslot"
        LOWSLOT = "Lowslot"
        RIGSLOT = "Rigslot"
        SERVICE = "Service"

    structure = models.ForeignKey(
        Structure,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Structure this item is located in",
    )

    eve_type = models.ForeignKey(
        EveType,
        on_delete=models.CASCADE,
        help_text="eve type of the item",
        related_name="+",
    )

    slot = models.CharField(max_length=255, choices=Slot.choices)

    def __str__(self) -> str:
        return str(self.eve_type.name)
