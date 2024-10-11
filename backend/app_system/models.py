from django.apps import apps
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import get_resolver


# Create your models here.
class RecurField(models.Model):
    objects = models.Manager()
    is_del = models.BooleanField(default=False)
    add_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(app_label)s%(class)sadd")
    modify_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(app_label)s%(class)schange")
    delete_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(app_label)s%(class)sdelete")
    add_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    delete_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class SystemConfiguration(RecurField):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ModuleConfiguration(RecurField):
    menu_type_choices = [
        ('drop-down', 'drop-down'),
        ('navigation', 'navigation'),
        ('route', 'route'),
    ]
    name = models.CharField(max_length=100)
    menu_type = models.CharField(max_length=50, choices=menu_type_choices)
    is_root_menu = models.BooleanField(default=False)
    page_url = models.URLField(null=True, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    children = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='parents')

    def __str__(self):
        return self.name


class CustomPermission(RecurField):
    element_type_choices = [
        ('Button', 'Button'),
    ]
    name = models.CharField(max_length=200)
    codename = models.CharField(max_length=100)
    element_type = models.CharField(max_length=100, choices=element_type_choices, null=True, blank=True)
    description = models.CharField(max_length=1000)
    is_common_for_all = models.BooleanField(default=False)

    users = models.ManyToManyField(User, blank=True, related_name='custom_permissions')
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_permissions')
    menu_items = models.ManyToManyField(ModuleConfiguration, blank=True, related_name='custom_permissions')

    def __str__(self):
        return self.name


"""
Employee(False)
Employee -> Employee Bank(True)
Master
 - Department
 - City
 - State
 - Country
Company
Company Branch
System Configuration

Google Review
Send Email
Send Whatsapp
Assign Task
"""







