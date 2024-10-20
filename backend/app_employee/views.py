from app_employee.models import Employee
from app_employee.serializers import EmployeeSerializer
from python_files.techno_generic import TechnoGenericAPIView


# Create your views here.
class EmployeeView(TechnoGenericAPIView):
    model = Employee
    serializer_class = EmployeeSerializer
    modules = ('Employee',)












