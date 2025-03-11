from django.urls import path

from app_permission.views import SideBarView, ModuleConfigurationView, DynamicModuleView

app_name = "permission"

urlpatterns = [
    path("sidebar/", SideBarView.as_view(), name="home"),
    path("module_configuration/", ModuleConfigurationView.as_view(), name="module_configuration"),
    path("dynamic_modules/<str:rec_id>/", DynamicModuleView.as_view(), name="dynamic_modules"),
]
