# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from scrapy.http import HtmlResponse
# import scrapy
# from urllib.parse import quote
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time

# class ShophiveSpider(scrapy.Spider):
#     name = 'shophive_query'
#     allowed_domains = ['shophive.com']
    
#     def __init__(self, query='', *args, **kwargs):
#         super(ShophiveSpider, self).__init__(*args, **kwargs)
#         self.start_urls = [f'https://www.shophive.com/catalogsearch/result/?q={quote(query)}']
        
#         chrome_options = Options()
#         chrome_options.add_argument("--headless=new")  
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
        
#         WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'product-item')]")))
        
#         html = self.driver.page_source
#         response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

#         products = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'product-item')]") 
        
#         for product in products:
#             if self.item_count >= 5:  
#                 break

#             name = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").text.strip() if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
#             price_element = product.find_element(By.CSS_SELECTOR, 'span.price-wrapper span.price') if product.find_elements(By.CSS_SELECTOR, 'span.price-wrapper span.price') else None
#             price = price_element.text.strip() if price_element else None
#             product_url = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").get_attribute("href") if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
#             image_url = product.find_element(By.CSS_SELECTOR, "img.product-image-photo").get_attribute("src") if product.find_elements(By.CSS_SELECTOR, "img.product-image-photo") else None

            
#             if price:
#                 try:
#                     price_cleaned = price.replace("Rs.", "").replace("Rs", "").replace(",", "").strip()
#                     price = float(price_cleaned)
#                 except ValueError:
#                     price = None

#             yield {
#                 'name': name,
#                 'price': price,
#                 'url': response.urljoin(product_url) if product_url else None,
#                 'image_url': image_url,
#                 'platform' : "Shophive",
#                 'category': "Electronics"
#             }

#             self.item_count += 1  

#     def closed(self):
#         self.driver.quit() 
