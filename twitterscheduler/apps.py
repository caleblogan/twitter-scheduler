from django.apps import AppConfig


class TwitterschedulerConfig(AppConfig):
    name = 'twitterscheduler'

    def ready(self):
        super().ready()
        from . import signals
