from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from app_system.models import *


# Register your models here.
class RecurAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display = (
                ("id",) + tuple(self.list_display) + ("add_by", "modify_by", "is_del")
        )
        self.list_filter = tuple(self.list_filter) + ("is_del",)
        self.list_editable = tuple(self.list_editable) + ("is_del",)

    def get_queryset(self, request):
        qs = self.model.admin_objects.get_queryset()
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


admin.site.register(SystemConfiguration, RecurAdmin)
admin.site.register(Permission)
admin.site.register(CustomUser, admin.ModelAdmin)


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'app_label', 'model']
