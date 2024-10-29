from django.urls import path

from app_employee.views import EmployeeView, DepartmentView

app_name = 'employee'

urlpatterns = [
    path('', EmployeeView.as_view(), name='home'),
    path('department/', DepartmentView.as_view(), name='department'),
]

