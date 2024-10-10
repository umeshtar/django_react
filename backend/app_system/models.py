from django.apps import apps
from django.contrib.auth.models import User, Group
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


class DjangoModelPermission(RecurField):
    codename = models.CharField(max_length=100)

    def __str__(self):
        return self.codename

    @staticmethod
    def allowed_permissions():
        return [
            f'{app}.{perm}_{model}'
            for app, model_dict in apps.all_models.items()
            if app.startswith('app_')
            for model in model_dict
            for perm in ['add', 'view', 'change', 'delete']
        ]
    
    def save(self, *args, **kwargs):
        if self.codename not in self.allowed_permissions():
            raise ValidationError('Invalid Permission')
        super().save(*args, **kwargs)
    

class MenuItem(RecurField):
    menu_type_choices = [
        ('drop-down', 'drop-down'),
        ('navigation', 'navigation'),
    ]
    name = models.CharField(max_length=100)
    menu_type = models.CharField(max_length=50, choices=menu_type_choices)
    is_main_menu = models.BooleanField(default=False)

    # for menu_type == 'navigation'
    page_url = models.URLField(null=True, blank=True)
    permissions = models.ManyToManyField(DjangoModelPermission, blank=True)

    # for drop-down and nested navigation
    children = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='parent_menu_items')

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
    menu_items = models.ManyToManyField(MenuItem, blank=True, related_name='custom_permissions')

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







