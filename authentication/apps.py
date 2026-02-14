from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"

    def ready(self):
        # Register drf-spectacular extensions.
        try:
            from . import openapi  # noqa: F401
        except Exception:
            # Never block app startup on docs helpers.
            pass
