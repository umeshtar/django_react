from django.apps import AppConfig


class AppDynamicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_dynamic'
