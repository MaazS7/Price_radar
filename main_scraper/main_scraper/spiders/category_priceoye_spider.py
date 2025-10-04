# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options  
# from scrapy.http import HtmlResponse
# import scrapy
# from urllib.parse import quote
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# class PriceOyeSpider(scrapy.Spider):
#     name = 'priceoye_category'
#     allowed_domains = ['priceoye.pk']
    
#     def __init__(self, *args, **kwargs):
#         super(PriceOyeSpider, self).__init__(*args, **kwargs)
#         self.start_urls = [f'https://priceoye.pk/mobiles/pricelist?brands=samsung_infinix_oppo_xiaomi_vivo_tecno_realme']
        
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")  
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

#         self.driver = webdriver.Chrome() 
#         self.driver.get("https://www.google.com") 
#         self.item_count = 0  

#     def parse(self, response):
#         print("Scraping started...")
#         self.driver.get(response.url)
        
#         WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.ga-dataset")))

#         html = self.driver.page_source
#         response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

#         products = response.css('a.ga-dataset')  
        
#         for product in products:
#             if self.item_count >= 3:  
#                 break

#             name = product.css('div.p-title.p-title-center::text').get()
#             price = product.css('div.price-box.p1 span::text').get()
#             if price:
#                 price = price.replace('Rs', '').replace(',', '').strip()  
#                 price = float(price) if price else None  
#             else:
#                 price = None  

#             product_url = product.css('::attr(href)').get()
#             image_url = product.css('img.product-thumbnail-img::attr(src)').get()

#             if not product_url:
#                 product_url = "https://priceoye.pk"
        
#             yield {
#                 'name': name.strip() if name else None,
#                 'price': price,
#                 'url': response.urljoin(product_url) if product_url else None,
#                 'image_url': image_url if image_url else None,
#                 'platform': "PriceOye",
#                 'category': "Electronics"
#             }

#             self.item_count += 1  

#         self.driver.quit()