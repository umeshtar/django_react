from django.urls import path

from app_dynamic.views import DynamicModuleView

app_name = "dynamic"

urlpatterns = [
    path("dynamic_modules/<str:rec_id>/", DynamicModuleView.as_view(), name="dynamic_modules"),
]
