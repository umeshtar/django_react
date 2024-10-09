from django.contrib import admin

from app_system.models import ModuleConfiguration, MenuItem, SystemConfiguration


# Register your models here.
class RecurAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display = ('id',) + self.list_display + ('is_del',)
        self.list_filter = self.list_filter + ('is_del',)
        self.list_editable = self.list_editable + ('is_del',)


admin.site.register(ModuleConfiguration, RecurAdmin)
admin.site.register(SystemConfiguration, RecurAdmin)


@admin.register(MenuItem)
class MenuItemAdmin(RecurAdmin):
    list_display = ('name', 'is_main_menu', 'menu_type', 'page_url')
    list_editable = ('is_main_menu',)









