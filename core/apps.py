from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Car Dealership Core'
    
    def ready(self):
        import core.templatetags.loan_filters  # noqa 