from django.db import models

from app_system.models import RecurField


# Create your models here.
class Country(RecurField):
    code = models.CharField(max_length=3)


class State(RecurField):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)


class City(RecurField):
    state = models.ForeignKey(State, on_delete=models.CASCADE)


class Company(RecurField):
    establish_date = models.DateField()
    city = models.ForeignKey(City, models.CASCADE)


class CompanyBranch(RecurField):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

