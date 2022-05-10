from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import __title__, urls


class StructureIntelMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _(__title__),
            "fas fa-user-secret fa-fw",
            "structureintel:index",
            navactive=["structureintel:"],
        )

    def render(self, request):
        if request.user.has_perm("structureintel.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return StructureIntelMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "structureintel", r"^structureintel/")
