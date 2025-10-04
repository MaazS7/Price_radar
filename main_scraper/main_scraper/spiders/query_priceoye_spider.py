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
#     name = 'priceoye_query_s'
#     allowed_domains = ['priceoye.pk']
    
#     def __init__(self, query='', *args, **kwargs):
#         super(PriceOyeSpider, self).__init__(*args, **kwargs)
#         self.start_urls = [f'https://priceoye.pk/search?q={quote(query)}']
        
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")  
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         # chrome_options.add_argument("--disable-gpu")
#         # chrome_options.add_argument("--window-size=1920,1080")
#         # chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

#         self.driver = webdriver.Chrome() 
#         self.driver.get("https://www.google.com") 
#         self.item_count = 0  

        

#     def parse(self, response):

#         print("Scraping started...")
#         self.driver.get(response.url)
        
#         WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.productBox.b-productBox")))

#         html = self.driver.page_source
#         response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

#         products = response.css('div.productBox.b-productBox')  
        
#         for product in products:
#             if self.item_count >= 3:  
#                 break

#             name = product.css('div.p-title.bold.h5::text').get()
#             price = response.css('div.price-box.p1 *::text').get()
#             if price:
#                 price = price.replace('Rs', '').replace(',', '').strip()  
#                 price = float(price) if price else None  
#             else:
#                 price = None  


#             product_url = product.css('a[href*="/mobiles/"]::attr(href)').get()
#             image_url = product.css('div.image-box amp-img::attr(src)').get()

#             if not product:
#                 product_url = "www.priceoye.pk"
        
#             yield {
#                 'name': name.strip() if name else None,
#                 'price': float(price.replace('Rs ', '').replace(',', '')) if price and price.replace('Rs ', '').strip() else None,
#                 'url': response.urljoin(product_url) if product_url else None,
#                 'image_url': image_url if image_url else None,
#                 'platform' : "PriceOye",
#                 'category': "Electronics"
#             }

#             self.item_count += 1  

#         self.driver.quit()