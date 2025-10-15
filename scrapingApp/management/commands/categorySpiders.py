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

        daraz_urls=[
            # "https://www.daraz.pk/catalog/?from=hp_categories&page=20&q=Smart%20Phones&service=all_channel",
            # "https://www.daraz.pk/catalog/?spm=a2a0e.searchlist.cate_5.10.44e02c3f9VJbIC&q=Laptops&from=hp_categories&src=all_channel",
            "https://www.daraz.pk/catalog/?spm=a2a0e.searchlist.cate_2.9.1a2e762fRU9g5n&q=Televisions&from=hp_categories&src=all_channel",
            "https://www.daraz.pk/catalog/?spm=a2a0e.pdp_revamp.cate_5.7.137a57f6CoqmIt&q=Smart%20Watches&from=hp_categories&src=all_channel",
        ]
        

        self.stdout.write(self.style.SUCCESS(f"🚀 Running Scrapy for query:"))

        process = CrawlerProcess(get_project_settings())
        process.crawl(DarazScraper, urls= daraz_urls)
        # time.sleep(20)
        # process.crawl(ShophiveSpider)
        # process.crawl(PriceOyeSpider)
        process.start(stop_after_crawl=True)

        self.stdout.write(self.style.SUCCESS(f"✅ Scrapy completed for query:"))