from django.urls import path

from app_permission.views import LayoutView, ModuleConfigurationView

app_name = "permission"

urlpatterns = [
    path("", LayoutView.as_view(), name="home"),
    path("module_configuration/", ModuleConfigurationView.as_view(), name="module_configuration"),
]
