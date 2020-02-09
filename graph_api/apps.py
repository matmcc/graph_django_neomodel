from importlib import import_module

from django.apps import AppConfig
from django.conf import settings


class GraphApiConfig(AppConfig):
    name = 'graph_api'

    def ready(self):
        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore()
        SessionStore.flush()

