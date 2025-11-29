from django.core.management import call_command
from django.http import JsonResponse
import time

def run():
    time.sleep(10)
    try:
        call_command('categorySpiders')
        return JsonResponse({'status' : 'success', 'message': 'Command for Spider run successfully'})
    except Exception as e:
        return JsonResponse({'status' : 'failed', 'message': str(e)}, status=500)