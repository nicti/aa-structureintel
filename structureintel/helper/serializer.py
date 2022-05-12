from django.urls import reverse
from django.utils.html import format_html
from eveuniverse.models import EveSolarSystem, EveType

from allianceauth.eveonline.evelinks.dotlan import solar_system_url
from allianceauth.eveonline.evelinks.eveimageserver import type_icon_url

from ..models import Structure, StructureModule


class StructureSerializer:
    def __init__(self, queryset) -> None:
        self.queryset = queryset

    def to_list(self, request) -> list:
        return [self.serialize_obj(obj, request) for obj in self.queryset]

    def serialize_obj(self, structure: Structure, request) -> dict:
        # Fetch services
        services = StructureModule.objects.filter(
            structure_id=structure.id, slot="Service"
        )
        servicesNames = []
        for service in services:
            servicesNames.append(service.eve_type.name)

        if request.user.has_perm("structureintel.delete_structure"):
            actions = format_html(
                '<button type="button" class="btn btn-default" data-toggle="modal" data-target="#modalStructureDetails" data-ajax_url="{}" title="Show fitting"><i class="fas fa-search"></i></button> <a class="btn btn-danger" href="{}" title="Delete structure"><i class="fas fa-trash"></i></button>',
                reverse("structureintel:structure_details", args=[structure.id]),
                reverse("structureintel:delete", args=[structure.id]),
            )
        else:
            actions = format_html(
                '<button type="button" class="btn btn-default" data-toggle="modal" data-target="#modalStructureDetails" data-ajax_url="{}" title="Show fitting"><i class="fas fa-search"></i></button>',
                reverse("structureintel:structure_details", args=[structure.id]),
            )
        return {
            "id": structure.id,
            "location": format_html(
                '<a href="{}" target="_blank">{}</a><br><a href="{}" target="_blank">{}</a>',
                solar_system_url(structure.eve_solar_system.id),
                structure.eve_solar_system.name,
                "https://evemaps.dotlan.net/map/"
                + str(
                    structure.eve_solar_system.eve_constellation.eve_region.name
                ).replace(" ", "_")
                + "/"
                + str(structure.eve_solar_system.name).replace(" ", "_"),
                structure.eve_solar_system.eve_constellation.eve_region.name,
            ),
            "type_icon": format_html(
                '<img src="{}" width="{}" height="{}"/>',
                type_icon_url(structure.eve_type.id, 32),
                32,
                32,
            ),
            "type": structure.eve_type.name,
            "structure_name": format_html("{}<br>{}", structure.name, structure.owner),
            "services": "<br>".join(servicesNames),
            "power": structure.get_power_mode_display(),
            "reinforcement": "{:02d}:00".format(structure.reinforce_hour),
            "actions": actions,
            "system_name": structure.eve_solar_system.name,
            "constellation_name": structure.eve_solar_system.eve_constellation.name,
            "region_name": structure.eve_solar_system.eve_constellation.eve_region.name,
        }


class SolarSystemSerializer:
    def __init__(self, queryset) -> None:
        self.queryset = queryset

    def to_list(self) -> list:
        return [self.serialize_obj(obj) for obj in self.queryset]

    def serialize_obj(self, solar: EveSolarSystem) -> dict:
        return {"id": solar.id, "text": solar.name}


class EveTypeSerializer:
    def __init__(self, queryset) -> None:
        self.queryset = queryset

    def to_list(self) -> list:
        return [self.serialize_obj(obj) for obj in self.queryset]

    def serialize_obj(self, type: EveType) -> dict:
        return {"id": type.id, "text": type.name}
