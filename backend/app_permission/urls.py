from django.urls import path

from app_permission.views import LayoutView

app_name = "permission"

urlpatterns = [
    path("", LayoutView.as_view(), name="home"),
]
