from django.urls import path

from app_employee.views import EmployeeView, DepartmentView, EmployeeBankView

app_name = 'employee'

urlpatterns = [
    path('', EmployeeView.as_view(), name='home'),
    path('department/', DepartmentView.as_view(), name='department'),
    path('bank/', EmployeeBankView.as_view(), name='bank'),
]

