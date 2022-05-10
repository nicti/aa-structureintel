from django.urls import path

from . import views

app_name = "structureintel"

urlpatterns = [
    path("", views.index, name="index"),
    path("list_data", views.structureintel_list_data, name="structureintel_list_data"),
    path("add_structure/", views.CreateStructureView.as_view(), name="add_structure"),
    path("solar_system", views.solar_system, name="solar_system"),
    path("structures", views.structures, name="structures"),
    path(
        "<int:structure_id>/structure_details",
        views.structure_details,
        name="structure_details",
    ),
    path("remove/<int:pk>", views.RemoveStructureView.as_view(), name="delete"),
]
