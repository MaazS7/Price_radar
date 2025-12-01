from django.apps import AppConfig
import threading


class ScrapingappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scrapingApp'

    # def ready(self):
    #     from scrapingApp import startup_task
    #     # Run the task in a background thread so Django startup isn't blocked
    #     threading.Thread(target=startup_task.startSchedular, daemon=True).start()