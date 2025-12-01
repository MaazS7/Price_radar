import os
import sys
from pathlib import Path
import multiprocessing
import time
# from twisted.internet import reactor, defer
# from scrapy.crawler import CrawlerRunner

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "main_scraper.main_scraper.settings")

from scrapy.crawler import CrawlerProcess
from django.core.management.base import BaseCommand
from scrapy.utils.project import get_project_settings
from main_scraper.main_scraper.spiders.category_spiders import DarazScraper, ShophiveSpider,PriceOyeSpider, MegaScraper
# from price_radar.main_scraper.main_scraper.spiders.category_spiders import ShophiveSpider
# from price_radar.main_scraper.main_scraper.spiders.category_spiders import PriceOyeSpider

# def run_spider_process(spider_class, urls):
#         """Function to run in separate process"""
#         process = CrawlerProcess(get_project_settings())
#         process.crawl(spider_class, urls=urls)
#         process.start(stop_after_crawl=True)


class Command(BaseCommand):
    help = 'Run Scrapy spiders'

    def add_arguments(self, parser):
        # parser.add_argument('query', type=str, help='Query to pass to spiders')
        pass
    

    def handle(self, *args, **kwargs):
        # query = kwargs['query']

        # Ensure Scrapy settings are loaded correctly

        daraz_urls=[
            "https://www.daraz.pk/catalog/?spm=a2a0e.pdp_revamp.cate_5.5.6d713b7e4mSfMr&q=Smart%20Phones&from=hp_categories&src=all_channel",
            "https://www.daraz.pk/catalog/?spm=a2a0e.searchlist.cate_5.10.44e02c3f9VJbIC&q=Laptops&from=hp_categories&src=all_channel",
            "https://www.daraz.pk/catalog/?spm=a2a0e.searchlist.cate_2.9.1a2e762fRU9g5n&q=Televisions&from=hp_categories&src=all_channel",
            "https://www.daraz.pk/catalog/?spm=a2a0e.pdp_revamp.cate_5.7.137a57f6CoqmIt&q=Smart%20Watches&from=hp_categories&src=all_channel",
            "https://www.daraz.pk/catalog/?q=Headphones%20%26%20Headsets&from=lp_category&src=all_channel&searchFlag=1&spm=a2a0e.categorylp.0.0",
            "https://www.daraz.pk/catalog/?q=Kitchen%20Appliances&from=lp_category&src=all_channel&searchFlag=1&spm=a2a0e.categorylp.0.0"
        ]

        priceOye_urls = [
            "https://priceoye.pk/smart-watches/pricelist?brands=faster_sveston_zero_assorted_dany_samsung_yolo_airox",
            "https://priceoye.pk/mobiles/pricelist?brands=samsung_infinix_oppo_xiaomi_vivo_tecno_realme_itel_apple_asus_blackberry_dcode_digit_google_honor_htc_huawei_lenovo_nokia_nothing_oneplus_qmobile_sego_sony_vgo-tel_motorola",
            "https://priceoye.pk/tablets/pricelist?sort=price_asc",
            "https://priceoye.pk/wireless-earbuds/pricelist?sort=price_asc",
            "https;//priceoye.pk/sale"
        ]

        shophive_urls = [
            "https://www.shophive.com/mobile-phones?manufacturer=apple,nokia,oneplus,oppo,philips,realme,samsung,sony,infinix,mi,honor,tecno,vivo,nothing,sego,dcode,itel",
            "https://www.shophive.com/smart-watches",
            "https://www.shophive.com/laptops-computers/laptops",
            "https://www.shophive.com/tv/led",
            "https://www.shophive.com/audio/headphones",
            "https://www.shophive.com/audio/earbuds",
            "https://www.shophive.com/shop/printers",
        ]
        
        mega_urls = [
            "https://www.mega.pk/mobiles/",
            "https://www.mega.pk/laptops/",
            "https://www.mega.pk/watches/",
            "https://www.mega.pk/ledtv/",
            "https://www.mega.pk/printer/",
        ]

        # spiders = [
        #     # (DarazScraper, daraz_urls),
        #     (PriceOyeSpider, priceOye_urls),
        #     (ShophiveSpider, shophive_urls),
        #     # (MegaScraper, mega_urls)
        # ]

        self.stdout.write(self.style.SUCCESS(f"🚀 Running Scraper"))

        process = CrawlerProcess(get_project_settings())
        process.crawl(DarazScraper, urls= daraz_urls)
        time.sleep(9000)
        process.crawl(ShophiveSpider, urls = shophive_urls)
        time.sleep(7200)
        process.crawl(PriceOyeSpider, urls = priceOye_urls)
        time.sleep(3600)
        process.crawl(MegaScraper, urls = mega_urls)
        process.start(stop_after_crawl=True)

        self.stdout.write(self.style.SUCCESS(f"✅ Scraping completed"))


        # for spider_class, urls in spiders:
        #     print(f"\n🚀 Starting {spider_class.__name__}...")
            
        #     # Create and start process
        #     p = multiprocessing.Process(
        #         target=run_spider_process,
        #         args=(spider_class, urls)
        #     )
        #     p.daemon = True
        #     p.start()
        #     timeout1 = 7200 if spider_class is DarazScraper else 3600

        #     p.join(timeout= timeout1)

        #     if p.is_alive():
        #         p.terminate()
        #         p.join(timeout=20)
            
        #     print(f"✅ {spider_class.__name__} completed")
            
        #     time.sleep(5)

        # print("\n🎊 All spiders completed!")