from django.contrib import admin

from app_permission.models import (
    CustomPermission,
    ModuleConfiguration,
    UserDefinedContentType, ReactBoxIcon,
)
from app_system.admin import RecurAdmin

# Register your models here.
admin.site.register(UserDefinedContentType, admin.ModelAdmin)
admin.site.register(CustomPermission, RecurAdmin)
admin.site.register(ReactBoxIcon, RecurAdmin)


@admin.register(ModuleConfiguration)
class ModuleConfigurationAdmin(RecurAdmin):
    list_display = ("name", "codename", "get_children", "get_parents", "is_root_menu", "menu_type", "sequence")
    list_editable = ("is_root_menu", "sequence")
    filter_horizontal = ("permissions",)

    def get_children(self, obj):
        return ", ".join([row.codename for row in obj.children.all()])

    def get_parents(self, obj):
        return ", ".join([row.codename for row in obj.parents.all()])

    get_children.short_description = "Children"
    get_parents.short_description = "Parents"
