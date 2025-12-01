from django.core.management import call_command
from django.http import JsonResponse
import time
from apscheduler.schedulers.background import BackgroundScheduler

def startSchedular():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run, 'cron', hour=2, minute=0)  # run after every 24 hours on 2 AM 
    scheduler.start()

def run():
    time.sleep(10)
    try:
        call_command('categorySpiders')
        return JsonResponse({'status' : 'success', 'message': 'Command for Spider run successfully'})
    except Exception as e:
        return JsonResponse({'status' : 'failed', 'message': str(e)}, status=500)