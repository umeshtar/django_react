from django.db import models

from app_system.models import RecurField


# Create your models here.
class Section(RecurField):
    pass


class Department(RecurField):
    sections = models.ManyToManyField(Section, blank=True)


class Employee(RecurField):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')


class EmployeeBank(RecurField):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)


class Candidate(RecurField):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='candidates')







