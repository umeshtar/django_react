from django.urls import path

from app_employee.views import DepartmentView, EmployeeView

app_name = "employee"

urlpatterns = [
    path("", EmployeeView.as_view(), name="employee"),
    path("department/", DepartmentView.as_view(), name="department"),
]
