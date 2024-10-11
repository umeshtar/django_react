from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from app_system.models import *


# Register your models here.
class RecurAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display = ('id',) + self.list_display + ('is_del',)
        self.list_filter = self.list_filter + ('is_del',)
        self.list_editable = self.list_editable + ('is_del',)


admin.site.register(SystemConfiguration, RecurAdmin)
admin.site.register(CustomPermission, RecurAdmin)
admin.site.register(Permission)
admin.site.register(ContentType)


@admin.register(ModuleConfiguration)
class ModuleConfigurationAdmin(RecurAdmin):
    list_display = ('name', 'is_root_menu', 'menu_type')
    list_editable = ('is_root_menu',)









