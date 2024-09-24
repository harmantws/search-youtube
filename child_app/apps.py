from django.apps import AppConfig


class ChildAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "child_app"
