from django.urls import path

from app_company.views import CompanyView

app_name = 'company'

urlpatterns = [
    path('', CompanyView.as_view(), name='home'),
]

