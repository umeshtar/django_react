from app_employee.models import *
from python_files.techno_generic import TechnoModelSerializer


class EmployeeSerializer(TechnoModelSerializer):
    class Meta:
        model = Employee
        fields = ['name', 'department']

    def techno_validate(self, attrs: dict):
        self.tsv.check_exists('name')


