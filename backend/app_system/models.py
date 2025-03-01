import os.path
import uuid

from django.conf import settings
from django.contrib.auth.models import Group, Permission, AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models

from python_files.techno_validators import validate_codename


# Create your managers here.
class RecurManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_del=False)


class AdminManager(models.Manager):
    pass


# Recur Model
class RecurField(models.Model):
    objects = RecurManager()
    admin_objects = AdminManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
        ordering = ['add_date']

    def __str__(self):
        return self.name


# User Model
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


# Permission Related Models

class ReactBoxIcon(RecurField):
    class_name = models.CharField(max_length=100)


class ModuleConfiguration(RecurField):
    """
    Main Table for Users and Permissions
        Usage of Django Built in Permission Table
        1. Django models crud permissions: view, add, change, delete
        2. Django models custom permissions: approve, reject, change_owner
        3. System Settings Permissions with System Configuration Model
        4. Dynamic Permission with Content Type for User defined Models (Not Final Yet)
        5. Custom Permissions by Separate table and relations to users and groups

    Important: By default in views, Django allows full access to all users
        Backend Steps for Checking Permissions
        1. IsAuthenticated and DjangoModelPermissions are default in settings.py
        2. DjangoModelPermissions check for add, change, delete for queryset.model
        3. TechnoModelPermission check for add, change, delete for specified model
        4. BasePermission check for custom permissions
        5. .has_perm check for user permissions using codename
        6. .has_model_perms check for specific model user permissions using permission name
        Combine all methods to obtain desired permission checks
    """
    menu_type_choices = [
        ('drop-down', 'drop-down'),
        ('navigation', 'navigation'),
        ('route', 'route'),
    ]
    codename = models.CharField(max_length=100, validators=[validate_codename])
    menu_type = models.CharField(max_length=50, choices=menu_type_choices)
    is_root_menu = models.BooleanField(default=False)
    page_url = models.URLField(null=True, blank=True)
    react_box_icon = models.ForeignKey(ReactBoxIcon, on_delete=models.PROTECT)
    permissions = models.ManyToManyField(Permission, blank=True)
    children = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='parents')


class CustomPermission(RecurField):
    element_type_choices = [
        ('Button', 'Button'),
        ('Select Box', 'Select Box'),
        ('Form Field', 'Form Field'),
        ('Filter Form Field', 'Filter Form Field'),
    ]
    perm_scope_choices = [
        ('Modules', 'Modules'),
        ('Global', 'Global'),
    ]
    codename = models.CharField(max_length=100)
    element_type = models.CharField(max_length=100, choices=element_type_choices, null=True, blank=True)
    perm_scope = models.CharField(max_length=20, choices=perm_scope_choices)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='custom_permissions')
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_permissions')
    modules = models.ManyToManyField(ModuleConfiguration, blank=True, related_name='custom_permissions')


class UserDefinedContentType(ContentType):
    """
    For Dynamic Board and Items with Crud, Customization and Permissions (Not Final Yet)
    """
    pass

