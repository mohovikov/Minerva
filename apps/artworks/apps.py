from django.apps import AppConfig


class ArtworksConfig(AppConfig):
    name = "apps.artworks"
    verbose_name = "Галерея"

    def ready(self):
        import apps.artworks.signals
