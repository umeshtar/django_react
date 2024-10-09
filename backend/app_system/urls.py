from django.urls import path

from app_system.views import IndexView

app_name = 'system'

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
]

