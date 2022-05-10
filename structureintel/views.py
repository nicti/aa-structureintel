from enum import IntEnum

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import CreateView, DeleteView
from eveuniverse.models import EveSolarSystem, EveType, EveTypeDogmaAttribute

from structureintel.forms import StructureForm
from structureintel.helper.serializer import (
    EveTypeSerializer,
    SolarSystemSerializer,
    StructureSerializer,
)

from .models import Structure, StructureModule


@login_required
@permission_required("structureintel.basic_access")
def index(request):
    return render(request, "structureintel/index.html")


@login_required
@permission_required("structureintel.basic_access")
def structureintel_list_data(request) -> JsonResponse:
    """Fetch view for structure list"""
    structures = Structure.objects.all()
    serializer = StructureSerializer(structures)
    return JsonResponse({"data": serializer.to_list(request)})


@login_required
@permission_required("structureintel.basic_access")
def solar_system(request) -> JsonResponse:
    term = request.GET.get("term")
    if not term:
        return JsonResponse({"data": []})
    queryset = EveSolarSystem.objects.all().filter(name__istartswith=term)
    return JsonResponse({"data": SolarSystemSerializer(queryset).to_list()})


@login_required
@permission_required("structureintel.basic_access")
def structures(request) -> JsonResponse:
    term = request.GET.get("term")
    if not term:
        return JsonResponse({"data": []})
    queryset = EveType.objects.all()
    queryset = queryset.filter(eve_group__eve_category_id=65, published=True)
    queryset = queryset.distinct().filter(name__icontains=term)
    return JsonResponse({"data": EveTypeSerializer(queryset).to_list()})


@login_required
@permission_required("structureintel.basic_access")
def structure_details(request, structure_id):
    class Slot(IntEnum):
        HIGH = 14
        MEDIUM = 13
        LOW = 12
        RIG = 1137
        SERVICE = 2056

        def image_url(self) -> str:
            """Return url to image file for this slot variant"""
            id_map = {
                self.HIGH: "h",
                self.MEDIUM: "m",
                self.LOW: "l",
                self.RIG: "r",
                self.SERVICE: "s",
            }
            try:
                slot_num = type_attributes[self.value]
                return staticfiles_storage.url(
                    f"structureintel/img/pannel/{slot_num}{id_map[self.value]}.png"
                )
            except KeyError:
                return ""

    structure: Structure = get_object_or_404(Structure, id=structure_id)

    type_attributes = {
        obj["eve_dogma_attribute_id"]: int(obj["value"])
        for obj in EveTypeDogmaAttribute.objects.filter(
            eve_type_id=structure.eve_type_id
        ).values("eve_dogma_attribute_id", "value")
    }
    slot_image_urls = {
        "high": Slot.HIGH.image_url(),
        "med": Slot.MEDIUM.image_url(),
        "low": Slot.LOW.image_url(),
        "rig": Slot.RIG.image_url(),
        "service": Slot.SERVICE.image_url(),
    }

    fittingModules = StructureModule.objects.filter(structure_id=structure.id)
    hSlotCounter = -1
    mSlotCounter = -1
    lSlotCounter = -1
    rSlotCounter = -1
    sSlotCounter = -1
    activeSlotCounter = None
    assets_grouped = {}
    assets = {"HiSlot": [], "MedSlot": [], "LoSlot": [], "RigSlot": [], "SerSlot": []}
    for fittingModule in fittingModules:
        slotStr = None
        if fittingModule.slot == StructureModule.Slot.HIGHSLOT:
            slotStr = "HiSlot"
            hSlotCounter = hSlotCounter + 1
            activeSlotCounter = hSlotCounter
        elif fittingModule.slot == StructureModule.Slot.MEDSLOT:
            slotStr = "MedSlot"
            mSlotCounter = mSlotCounter + 1
            activeSlotCounter = mSlotCounter
        elif fittingModule.slot == StructureModule.Slot.LOWSLOT:
            slotStr = "LoSlot"
            lSlotCounter = lSlotCounter + 1
            activeSlotCounter = lSlotCounter
        elif fittingModule.slot == StructureModule.Slot.RIGSLOT:
            slotStr = "RigSlot"
            rSlotCounter = rSlotCounter + 1
            activeSlotCounter = rSlotCounter
        elif fittingModule.slot == StructureModule.Slot.SERVICE:
            slotStr = "SerSlot"
            sSlotCounter = sSlotCounter + 1
            activeSlotCounter = sSlotCounter
        if slotStr:
            assets_grouped[slotStr + str(activeSlotCounter)] = {
                "eve_type_id": fittingModule.eve_type.id,
                "eve_type": {"name": fittingModule.eve_type.name},
            }
            assets[slotStr].append(
                {"id": fittingModule.eve_type.id, "name": fittingModule.eve_type.name}
            )
    context = {
        "system": structure.eve_solar_system.name,
        "name": structure.name,
        "slots": slot_image_urls,
        "assets_grouped": assets_grouped,
        "assets": assets,
        "structure": {
            "name": structure.eve_type.name,
            "eve_type_id": structure.eve_type.id,
        },
    }
    return render(request, "structureintel/structure_details.html", context)


class AddUpdateMixin:
    def get_form_kwargs(self):
        """Inject the request user into the kwargs passed to the form."""
        kwargs = super().get_form_kwargs()
        # kwargs.update({"user": self.request.user})
        return kwargs


class StructureManagementView(LoginRequiredMixin, PermissionRequiredMixin, View):
    model = Structure
    form_class = StructureForm
    title = "Edit Structure"


class CreateStructureView(StructureManagementView, AddUpdateMixin, CreateView):
    template_name_suffix = "_create_form"
    permission_required = "structureintel.basic_access"
    title = "Create New Structure"


class RemoveStructureView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Structure
    permission_required = (
        "structureintel.basic_access",
        "structureintel.delete_structure",
    )

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()
