from django.apps import AppConfig


class JugadoresConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jugadores"

    def ready(self):
        import jugadores.signals
