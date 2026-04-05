from django.apps import AppConfig


class ResultsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'results'

    def ready(self):
        """
        ready() is called once when Django finishes loading all apps.
        This is the correct place to import and connect signals.
        Importing signals here (not at module level) avoids circular imports.
        """
        import results.signals  # noqa: F401 — import triggers @receiver decorators
