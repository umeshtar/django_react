from django.contrib import admin

from app_company.models import *
from app_system.admin import RecurAdmin

# Register your models here.
admin.site.register(Country, RecurAdmin)
admin.site.register(State, RecurAdmin)
admin.site.register(City, RecurAdmin)
admin.site.register(Company, RecurAdmin)
admin.site.register(CompanyBranch, RecurAdmin)



