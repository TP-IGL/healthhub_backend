from django.apps import AppConfig


class HealthhubBackConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "healthhub_back"

    def ready(self):
        import healthhub_back.signals