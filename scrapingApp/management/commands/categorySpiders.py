import os
import sys
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "main_scraper.main_scraper.settings")

from scrapy.crawler import CrawlerProcess
from django.core.management.base import BaseCommand
from scrapy.utils.project import get_project_settings
from main_scraper.main_scraper.spiders.category_spiders import DarazScraper, ShophiveSpider,PriceOyeSpider
# from price_radar.main_scraper.main_scraper.spiders.category_spiders import ShophiveSpider
# from price_radar.main_scraper.main_scraper.spiders.category_spiders import PriceOyeSpider


class Command(BaseCommand):
    help = 'Run Scrapy spiders'

    def add_arguments(self, parser):
        # parser.add_argument('query', type=str, help='Query to pass to spiders')
        pass

    def handle(self, *args, **kwargs):
        # query = kwargs['query']

        # Ensure Scrapy settings are loaded correctly
        

        self.stdout.write(self.style.SUCCESS(f"🚀 Running Scrapy for query:"))

        process = CrawlerProcess(get_project_settings())
        # process.crawl(DarazScraper)
        # time.sleep(20)
        process.crawl(ShophiveSpider)
        # process.crawl(PriceOyeSpider)
        process.start(stop_after_crawl=True)

        self.stdout.write(self.style.SUCCESS(f"✅ Scrapy completed for query:"))