from django.urls import path

from app_permission.views import SideBarView, ModuleConfigurationView

app_name = "permission"

urlpatterns = [
    path("sidebar/", SideBarView.as_view(), name="home"),
    path("module_configuration/", ModuleConfigurationView.as_view(), name="module_configuration"),
]
