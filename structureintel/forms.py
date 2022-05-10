import re

from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.html import format_html
from eveuniverse.models import EveSolarSystem, EveType

from structureintel.models import Structure, StructureModule


class StructureForm(forms.ModelForm):
    ASTERISK_HTML = '<i class="fas fa-asterisk"></i>'

    eve_solar_system_2 = forms.CharField(
        required=True,
        label=format_html(f"Solar System {ASTERISK_HTML}"),
        widget=forms.Select(attrs={"class": "select2-solar-systems"}),
    )
    eve_structure_type_2 = forms.CharField(
        required=True,
        label=format_html(f"Structure Type {ASTERISK_HTML}"),
        widget=forms.Select(attrs={"class": "select2-structure-types"}),
    )
    mode = forms.ChoiceField(
        required=True, choices=Structure.PowerMode.choices, widget=forms.Select()
    )
    reinforcement_hour = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        widget=forms.NumberInput(attrs={"min": 0, "max": 23}),
    )
    fitting = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 5}))

    field_order = [
        "eve_solar_system_2",
        "eve_structure_type_2",
        "name",
        "owner",
        "mode",
        "reinforcement_hour",
        "fitting",
    ]

    class Meta:
        model = Structure
        fields = {
            "eve_solar_system_2",
            "eve_structure_type_2",
            "name",
            "owner",
            "mode",
            "reinforcement_hour",
            "fitting",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        if "instance" in kwargs and kwargs["instance"] is not None:
            my_instance = kwargs["instance"]
            self.is_new = False
        else:
            my_instance = None
            self.is_new = True

        super().__init__(*args, **kwargs)
        if my_instance:
            self.fields["eve_solar_system_2"].widget.choices = [
                (
                    str(my_instance.eve_solar_system_id),
                    my_instance.eve_solar_system.name,
                )
            ]
            self.fields["eve_structure_type_2"].widget.choices = [
                (str(my_instance.structure_type_id), my_instance.structure_type.name)
            ]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("eve_solar_system_2"):
            try:
                solar_system = EveSolarSystem.objects.get(
                    id=cleaned_data["eve_solar_system_2"]
                )
            except EveSolarSystem.DoesNotExist:
                pass
            else:
                self.fields["eve_solar_system_2"].widget.choices = [
                    (str(solar_system.id), solar_system.name)
                ]

        if cleaned_data.get("eve_structure_type_2"):
            try:
                structure_type = EveType.objects.get(
                    id=cleaned_data["eve_structure_type_2"]
                )
            except EveType.DoesNotExist:
                pass
            else:
                self.fields["eve_structure_type_2"].widget.choices = [
                    (str(structure_type.id), structure_type.name)
                ]

    def save(self, commit=True):
        # Store default fields
        structure: Structure = super().save(commit=False)
        # Store custom fields
        structure.power_mode = self.cleaned_data.get("mode")
        structure.eve_solar_system_id = self.cleaned_data.get("eve_solar_system_2")
        structure.eve_type_id = self.cleaned_data.get("eve_structure_type_2")
        structure.reinforce_hour = self.cleaned_data.get("reinforcement_hour")
        fitting = self.cleaned_data.get("fitting")
        # Parse fitting
        fitting_data = fitting.replace("\r\n", "\n")
        highslots = None
        # Fitting has high slots
        if "High Power Slots" in fitting_data:
            # Assume High and Med slots are fitted
            highslots = re.search(
                "High Power Slots\n(.*?)Medium Power Slots", fitting_data, re.M | re.S
            )
            if not highslots:
                # Assume High and Low slots are fitted
                highslots = re.search(
                    "High Power Slots\n(.*?)Low Power Slots", fitting_data, re.M | re.S
                )
                if not highslots:
                    # Assume High and Rig slots are fitted
                    highslots = re.search(
                        "High Power Slots\n(.*?)Rig Slots", fitting_data, re.M | re.S
                    )
                    if not highslots:
                        # Assume High and Service slots are fitted
                        highslots = re.search(
                            "High Power Slots\n(.*?)Service Slots",
                            fitting_data,
                            re.M | re.S,
                        )
                        if not highslots:
                            highslots = fitting_data.replace("High Power Slots\n", "")
        if type(highslots) == re.Match:
            highslots = highslots.group(1)

        mediumslots = None
        # Fitting has med slots
        if "Medium Power Slots" in fitting_data:
            # Assume Medium and Low slots are fitted
            mediumslots = re.search(
                "Medium Power Slots\n(.*?)Low Power Slots", fitting_data, re.M | re.S
            )
            if not mediumslots:
                # Assume Medium and Low slots are fitted
                mediumslots = re.search(
                    "Medium Power Slots\n(.*?)Rig Slots", fitting_data, re.M | re.S
                )
                if not mediumslots:
                    # Assume Medium and Rig slots are fitted
                    mediumslots = re.search(
                        "Medium Power Slots\n(.*?)Service Slots",
                        fitting_data,
                        re.M | re.S,
                    )
                    if not mediumslots:
                        mediumslots = fitting_data.replace("Medium Power Slots\n", "")
        if type(mediumslots) == re.Match:
            mediumslots = mediumslots.group(1)

        lowslots = None
        # Fitting has low slots
        if "Low Power Slots" in fitting_data:
            # Assume Low and rig slots are fitted
            lowslots = re.search(
                "Low Power Slots\n(.*?)Rig Slots", fitting_data, re.M | re.S
            )
            if not lowslots:
                # Assume Low and Service slots are fitted
                lowslots = re.search(
                    "Low Power Slots\n(.*?)Service Slots", fitting_data, re.M | re.S
                )
                if not lowslots:
                    lowslots = fitting_data.replace("Low Power Slots\n", "")
        if type(lowslots) == re.Match:
            lowslots = lowslots.group(1)

        rigslots = None
        # Fitting has rig slots
        if "Rig Slots" in fitting_data:
            # Assume Rig and Service slots are fitted
            rigslots = re.search(
                "Rig Slots\n(.*?)Service Slots", fitting_data, re.M | re.S
            )
            if not rigslots:
                rigslots = fitting_data.replace("Low Power Slots\n", "")
        if type(rigslots) == re.Match:
            rigslots = rigslots.group(1)

        serviceslots = None
        # Fitting has service slots
        if "Service Slots" in fitting_data:
            serviceslots = fitting_data.split("Service Slots\n")[1]

        # Save structure so related objects can be stored
        if commit:
            structure.save()

        # Store fitting mods

        if highslots:
            modules = highslots.strip().split("\n")
            for module in modules:
                evemodule = EveType.objects.get(name=module)
                fittingmodule = StructureModule()
                fittingmodule.eve_type_id = evemodule.id
                fittingmodule.slot = StructureModule.Slot.HIGHSLOT
                fittingmodule.structure_id = structure.id
                fittingmodule.save()

        if mediumslots:
            modules = mediumslots.strip().split("\n")
            for module in modules:
                evemodule = EveType.objects.get(name=module)
                fittingmodule = StructureModule()
                fittingmodule.eve_type_id = evemodule.id
                fittingmodule.slot = StructureModule.Slot.MEDSLOT
                fittingmodule.structure_id = structure.id
                fittingmodule.save()

        if lowslots:
            modules = lowslots.strip().split("\n")
            for module in modules:
                evemodule = EveType.objects.get(name=module)
                fittingmodule = StructureModule()
                fittingmodule.eve_type_id = evemodule.id
                fittingmodule.slot = StructureModule.Slot.LOWSLOT
                fittingmodule.structure_id = structure.id
                fittingmodule.save()

        if rigslots:
            modules = rigslots.strip().split("\n")
            for module in modules:
                evemodule = EveType.objects.get(name=module)
                fittingmodule = StructureModule()
                fittingmodule.eve_type_id = evemodule.id
                fittingmodule.slot = StructureModule.Slot.RIGSLOT
                fittingmodule.structure_id = structure.id
                fittingmodule.save()

        if serviceslots:
            modules = serviceslots.strip().split("\n")
            for module in modules:
                evemodule = EveType.objects.get(name=module)
                fittingmodule = StructureModule()
                fittingmodule.eve_type_id = evemodule.id
                fittingmodule.slot = StructureModule.Slot.SERVICE
                fittingmodule.structure_id = structure.id
                fittingmodule.save()
        return structure
