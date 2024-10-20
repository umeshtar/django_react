from app_employee.models import *
from python_files.techno_generic import TechnoModelSerializer


class EmployeeSerializer(TechnoModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'department', 'add_by']


