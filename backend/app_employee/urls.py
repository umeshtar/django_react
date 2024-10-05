from django.urls import path

from app_employee.views import EmployeeView

app_name = 'employee'

urlpatterns = [
    path('', EmployeeView.as_view(), name='home'),
]

