from django.apps import AppConfig


class MoverConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mover'

    # def ready(self):
    #     import apps.mover.signals
