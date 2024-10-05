from django.db import models

from app_system.models import RecurField


# Create your models here.
class Department(RecurField):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Employee(RecurField):
    name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        return self.name





