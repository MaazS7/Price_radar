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
# from django.core.management.base import BaseCommand
from scrapy.utils.project import get_project_settings
from main_scraper.main_scraper.spiders.single_product_spider import DarazPlaywrightSpider
# from price_radar.main_scraper.main_scraper.spiders.query_shophive_spider import ShophiveSpider
# from price_radar.main_scraper.main_scraper.spiders.query_shophive_spider import ShophiveSpider


class Command(BaseCommand):
    help = 'Run Scrapy spiders with a query'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='Query to pass to spiders')

    def handle(self, *args, **kwargs):
        query = kwargs['query']

        # Ensure Scrapy settings are loaded correctly
        

        self.stdout.write(self.style.SUCCESS(f"🚀 Running Scrapy for query: {query}"))

        process = CrawlerProcess(get_project_settings())
        if query.find("daraz"):
            process.crawl(DarazPlaywrightSpider, query=query)
            # time.sleep(20)
            # process.crawl(ShophiveSpider, query=query)
            # process.crawl(PriceOyeSpider, query=query)
            process.start(stop_after_crawl=True)

        self.stdout.write(self.style.SUCCESS(f"✅ Scrapy completed for query: {query}"))