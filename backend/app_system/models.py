from django.contrib.auth.models import User
from django.db import models


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







