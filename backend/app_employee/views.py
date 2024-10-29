from app_employee.models import Employee, Department
from app_employee.serializers import EmployeeSerializer, DepartmentSerializer
from python_files.techno_generic import TechnoGenericAPIView


# Create your views here.
class EmployeeView(TechnoGenericAPIView):
    model = Employee
    serializer_class = EmployeeSerializer
    modules = ('Employee',)


class DepartmentView(TechnoGenericAPIView):
    model = Department
    serializer_class = DepartmentSerializer
    modules = ('Department',)










