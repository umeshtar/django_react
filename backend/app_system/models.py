import os.path

import uuid
from django.conf import settings
from django.contrib.auth.models import Group, Permission, AbstractUser
from django.db import models


class RecurManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_del=False)


class AdminManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()


# Create your models here.
class RecurField(models.Model):
    objects = RecurManager()
    admin_objects = AdminManager()
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    add_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name="%(app_label)s%(class)s_add")
    modify_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="%(app_label)s%(class)s_change")
    delete_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="%(app_label)s%(class)s_delete")
    add_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    delete_date = models.DateTimeField(null=True, blank=True)
    is_del = models.BooleanField(default=False)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.username

    def has_model_perms(self, model, *perms, key='all'):
        if self.is_active and self.is_superuser:
            return True

        if not perms:
            perms = ('view', 'add', 'change', 'delete')

        app_label = model._meta.app_label
        model_name = model._meta.model_name
        perm_code = f"{app_label}.{{perm}}_{model_name}"

        func = any if key == 'any' else all
        return func([self.has_perm(perm_code.format(perm=perm)) for perm in perms])


class SystemConfiguration(RecurField):
    pass


class ReactBoxIcon(RecurField):
    class_name = models.CharField(max_length=100)


class ModuleConfiguration(RecurField):
    menu_type_choices = [
        ('drop-down', 'drop-down'),
        ('navigation', 'navigation'),
        ('route', 'route'),
    ]
    codename = models.CharField(max_length=100)
    menu_type = models.CharField(max_length=50, choices=menu_type_choices)
    is_root_menu = models.BooleanField(default=False)
    page_url = models.URLField(null=True, blank=True)
    react_box_icon = models.ForeignKey(ReactBoxIcon, on_delete=models.PROTECT, null=True, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    children = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='parents')


class CustomPermission(RecurField):
    element_type_choices = [
        ('Button', 'Button'),
        ('Select Box', 'Select Box'),
    ]
    perm_scope_choices = [
        ('Modules', 'Modules'),
        ('Global', 'Global'),
        ('System Setup', 'System Setup'),
    ]
    codename = models.CharField(max_length=100)
    element_type = models.CharField(max_length=100, choices=element_type_choices, null=True, blank=True)
    perm_scope = models.CharField(max_length=20, choices=perm_scope_choices)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='custom_permissions')
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_permissions')
    modules = models.ManyToManyField(ModuleConfiguration, blank=True, related_name='custom_permissions')


def get_path(instance, filename):
    return os.path.join(instance.name, filename)


class Attachment(RecurField):
    file = models.FileField(upload_to=get_path)




