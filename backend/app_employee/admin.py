from django.contrib import admin

from app_employee.models import Employee, Department, EmployeeBank
from app_system.admin import RecurAdmin


# Register your models here.
admin.site.register(Employee, RecurAdmin)
admin.site.register(Department, RecurAdmin)
admin.site.register(EmployeeBank, RecurAdmin)






