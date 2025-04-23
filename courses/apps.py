from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'
    
    def ready(self):
        """Importar señales al iniciar la aplicación."""
        import courses.signals  # Importar el módulo de señales
