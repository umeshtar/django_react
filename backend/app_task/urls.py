from django.urls import path

from app_system.views import IndexView

app_name = 'task'

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
]

