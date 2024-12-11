from django.urls import path

from app_employee.views import DepartmentView

app_name = 'employee'

urlpatterns = [
    path('department/', DepartmentView.as_view(), name='department'),
]

