from django.db import models

from app_system.models import RecurField


# Create your models here.
class Country(RecurField):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)


class State(RecurField):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)


class City(RecurField):
    name = models.CharField(max_length=50)
    state = models.ForeignKey(State, on_delete=models.CASCADE)


class Company(RecurField):
    name = models.CharField(max_length=50)
    establish_date = models.DateField()
    city = models.ForeignKey(City, models.CASCADE)

    def __str__(self):
        return self.name


class CompanyBranch(RecurField):
    name = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

