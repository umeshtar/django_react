from django.contrib import admin

from app_employee.models import *
from app_system.admin import RecurAdmin


# Register your models here.
admin.site.register(Employee, RecurAdmin)
admin.site.register(Candidate, RecurAdmin)
admin.site.register(Department, RecurAdmin)
admin.site.register(EmployeeBank, RecurAdmin)
admin.site.register(Section, RecurAdmin)






