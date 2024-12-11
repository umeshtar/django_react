from django.db import models

from app_system.models import RecurField


# Create your models here.
class Department(RecurField):
    pass


class Employee(RecurField):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')







