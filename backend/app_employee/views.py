from rest_framework.response import Response
from rest_framework.views import APIView

from app_employee.models import Employee, Department, EmployeeBank


# Create your views here.
class EmployeeView(APIView):
    model = Employee

    def get(self, request, *args, **kwargs):
        return Response({'data': f'Hello World {request.user} {request.user.is_authenticated}'})


class DepartmentView(APIView):
    model = Department

    def get(self, request, *args, **kwargs):
        return Response({'data': f'Department'})


class EmployeeBankView(APIView):
    model = EmployeeBank

    def get(self, request, *args, **kwargs):
        return Response({'data': 'Employee Bank'})











