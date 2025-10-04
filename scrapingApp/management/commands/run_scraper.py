import os
import sys
from pathlib import Path
# import time

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "main_scraper.main_scraper.settings")

from scrapy.crawler import CrawlerProcess
from django.core.management.base import BaseCommand
from scrapy.utils.project import get_project_settings
from main_scraper.main_scraper.spiders.query_spiders import DarazScraper, ShophiveSpider


class Command(BaseCommand):
    help = 'Run Scrapy spiders with a query'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='Query to pass to spiders')

    def handle(self, *args, **kwargs):
        query = kwargs['query']

        # Ensure Scrapy settings are loaded correctly
        

        self.stdout.write(self.style.SUCCESS(f"🚀 Running Scrapy for query: {query}"))

        process = CrawlerProcess(get_project_settings())
        process.crawl(DarazScraper, query=query)
        # time.sleep(20)
        process.crawl(ShophiveSpider, query=query)
        # process.crawl(PriceOyeSpider, query=query)
        process.start(stop_after_crawl=True)

        self.stdout.write(self.style.SUCCESS(f"✅ Scrapy completed for query: {query}"))

# class Command(BaseCommand):
#     help = 'Run Scrapy spiders with a query'

#     def add_arguments(self, parser):
#         parser.add_argument('query', type=str, help='Query to pass to spiders')

#     def handle(self, *args, **kwargs):
#         query = kwargs['query']

#         os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "price_radar.main_scraper.settings")

#         process = CrawlerProcess(get_project_settings())
#         process.crawl(DarazScraper, query=query)
#        # process.crawl(SpiderTwo, query=query)
#         process.start(stop_after_crawl=True)  # Starts the spiders

# import sys
# # import os
# # from pathlib import Path
# from twisted.internet import reactor
# from scrapy.crawler import CrawlerProcess
# from django.core.management.base import BaseCommand
# from scrapy.utils.project import get_project_settings
# from main_scraper.main_scraper.spiders.daraz_spider import DarazScraper
# from main_scraper.main_scraper.spiders.shophive_spider import ShophiveSpider
# from main_scraper.main_scraper.spiders.priceoye_spider import PriceOyeSpider

# class Command(BaseCommand):
#     help = 'Run Scrapy spiders with a query'

#     def add_arguments(self, parser):
#         parser.add_argument('query', type=str, help='Query to pass to spiders')
#         parser.add_argument('--session-key', type=str, help='Django session key for status updates')

#     def handle(self, *args, **kwargs):
#         query = kwargs['query']
#         session_key = kwargs.get('session_key')
        
#         # Setup session status tracking
#         if session_key:
#             from django.contrib.sessions.models import Session
#             from django.contrib.sessions.backends.db import SessionStore
#             session = SessionStore(session_key=session_key)
#             session['scraping_status'] = 'running'
#             session.save()
        
#         try:
#             # Initialize crawler process
#             process = CrawlerProcess(get_project_settings())
            
#             # Run spiders
#             process.crawl(DarazScraper, query=query)
#             process.crawl(ShophiveSpider, query=query)
#             # process.crawl(PriceOyeSpider, query=query)
            
#             # Set timeout (3 minutes total)
#             reactor.callLater(180, process.stop)
#             process.start()
            
#             # Update session on success
#             if session_key:
#                 session = SessionStore(session_key=session_key)
#                 session['scraping_status'] = 'completed'
#                 session.save()
            
#             self.stdout.write(self.style.SUCCESS(f"✅ Successfully scraped for: {query}"))
            
#         except Exception as e:
#             # Update session on failure
#             if session_key:
#                 session = SessionStore(session_key=session_key)
#                 session['scraping_status'] = 'failed'
#                 session['scraping_error'] = str(e)
#                 session.save()
                
#             self.stdout.write(self.style.ERROR(f"❌ Scraping failed: {str(e)}"))
#             if reactor.running:
#                 reactor.stop()
#             raise

# import sys
# from twisted.internet import reactor, task
# from scrapy.crawler import CrawlerRunner
# from django.core.management.base import BaseCommand
# from scrapy.utils.project import get_project_settings
# from main_scraper.main_scraper.spiders.daraz_spider import DarazScraper
# from main_scraper.main_scraper.spiders.shophive_spider import ShophiveSpider
# from main_scraper.main_scraper.spiders.priceoye_spider import PriceOyeSpider
# from twisted.internet.defer import inlineCallbacks, Deferred
# import time
# from django.core.cache import cache

# from twisted.internet import reactor, defer
# from django.core.management.base import BaseCommand
# from scrapy.crawler import CrawlerRunner
# from scrapy.utils.project import get_project_settings

# class Command(BaseCommand):
#     help = 'Run product scrapers with status tracking'

#     def add_arguments(self, parser):
#         parser.add_argument('query', type=str)
#         parser.add_argument('--cache-key', type=str)
#         parser.add_argument('--delay', type=int, default=120)

#     def handle(self, *args, **options):
#         """Wrap async execution in synchronous Django command"""
#         self._run_spiders(options)
#         reactor.run()  # Start the Twisted reactor

#     def _run_spiders(self, options):
#         """Async spider execution"""
#         query = options['query']
#         cache_key = options['cache_key']
#         delay = options['delay']
        
#         runner = CrawlerRunner(get_project_settings())
        
#         @defer.inlineCallbacks
#         def crawl():
#             try:
#                 self.update_status(cache_key, 'running', {
#                     'current_spider': None,
#                     'progress': '0/2'
#                 })
                
#                 spiders = [
#                     ('daraz', DarazScraper),
#                     ('shophive', ShophiveSpider)
#                 ]
                
#                 for i, (name, spider) in enumerate(spiders):
#                     self.update_status(cache_key, 'running', {
#                         'current_spider': name,
#                         'progress': f"{i+1}/{len(spiders)}"
#                     })
                    
#                     yield runner.crawl(spider, query=query)
                    
#                     if i < len(spiders) - 1:
#                         self.update_status(cache_key, 'waiting', {
#                             'next_spider': spiders[i+1][0],
#                             'wait_time': delay
#                         })
#                         yield task.deferLater(reactor, delay, lambda: None)
                
#                 self.update_status(cache_key, 'completed', {
#                     'completed_at': time.time(),
#                     'message': 'All spiders finished'
#                 })
                
#             except Exception as e:
#                 self.update_status(cache_key, 'failed', {
#                     'error': str(e),
#                     'failed_at': time.time()
#                 })
#                 self.stderr.write(f"Error: {str(e)}")
#             finally:
#                 reactor.stop()
        
#         crawl()  # Start the async process

#     def update_status(self, cache_key, status, extra=None):
#         """Update status in cache with timestamp"""
#         data = {
#             'status': status,
#             'last_update': time.time()
#         }
#         if extra:
#             data.update(extra)
#         cache.set(cache_key, data, timeout=3600)


# # Calculate paths - adjust based on your exact structure
# DJANGO_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # Goes up to price_radar/
# SCRAPY_ROOT = DJANGO_ROOT / "main_scraper" / "main_scraper"

# # Add to Python path
# sys.path.extend([
#     str(DJANGO_ROOT),      # price_radar/
#     str(SCRAPY_ROOT),      # price_radar/main_scraper/
# ])

# class Command(BaseCommand):
#     help = 'Run Scrapy spiders with a query'

#     def add_arguments(self, parser):
#         parser.add_argument('query', type=str, help='Query to pass to spiders')

#     def handle(self, *args, **kwargs):
#         query = kwargs['query']
        
#         try:
#             # Set the correct settings module path
#             # os.environ['SCRAPY_SETTINGS_MODULE'] = 'main_scraper.main_scraper.settings'
            
#             # Import spiders after setting the path
            
#             # Initialize crawler process
#             process = CrawlerProcess(get_project_settings())
            
#             # Run spiders
#             process.crawl(DarazScraper, query=query)
#             process.crawl(ShophiveSpider, query=query)
#             # process.crawl(PriceOyeSpider, query=query)
            
#             # Set timeout (3 minutes total)
#             reactor.callLater(180, process.stop)
#             process.start()
            
#             self.stdout.write(self.style.SUCCESS(f"✅ Successfully scraped for: {query}"))
            
#         except ImportError as e:
#             self.stdout.write(self.style.ERROR(f"❌ Import error: {str(e)}"))
#             self.stdout.write(f"Current Python path: {sys.path}")
#             raise
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f"❌ Scraping failed: {str(e)}"))
#             if reactor.running:
#                 reactor.stop()
#             raise