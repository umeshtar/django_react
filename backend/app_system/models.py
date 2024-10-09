from django.contrib.auth.models import User
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


class ModuleConfiguration(RecurField):
    url_name = models.CharField(max_length=100)

    def __str__(self):
        return self.url_name

    @staticmethod
    def allowed_url_names():
        url_patterns = get_resolver().url_patterns
        urls = []
        app_names = ['system', 'employee']

        def collect_urls(urlpatterns, app_name):
            for pattern in urlpatterns:
                if hasattr(pattern, 'url_patterns'):
                    if pattern.app_name in app_names:
                        collect_urls(pattern.url_patterns, pattern.app_name)
                elif app_name:
                    urls.append(f'{app_name}:{pattern.name}')
        collect_urls(url_patterns, '')
        return urls

    def save(self, *args, **kwargs):
        if self.url_name not in self.allowed_url_names():
            raise ValidationError('url_name is not valid')
        super().save(*args, **kwargs)


class MenuItem(RecurField):
    menu_type_choices = [
        ('drop-down', 'drop-down'),
        ('navigation', 'navigation'),
        ('route', 'route'),
    ]
    name = models.CharField(max_length=100)
    menu_type = models.CharField(max_length=50, choices=menu_type_choices)
    is_main_menu = models.BooleanField(default=False)

    # for menu_type == 'navigation' or 'route'
    page_url = models.URLField(null=True, blank=True)
    modules = models.ManyToManyField(ModuleConfiguration, blank=True)
    routes = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='route_menu_items')

    # for menu_type == 'drop-down'
    children = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='child_menu_items')

    def __str__(self):
        return self.name


# Example
"""
Dashboard
Employee (Employee Overview -> Experience For -> Bank)
Company
Company Branch
Master
- City
- Department
- Designation
"""


class SystemConfiguration(RecurField):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name











