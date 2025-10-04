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
#     name = 'shophive_category'
#     allowed_domains = ['shophive.com']
    
#     def __init__(self, *args, **kwargs):
#         super(ShophiveSpider, self).__init__(*args, **kwargs)
#         self.start_urls = [f'https://www.shophive.com/mobile-phones']
        
#         chrome_options = Options()
#         chrome_options.add_argument("--headless=new")  
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

#         self.driver = webdriver.Chrome(options=chrome_options)  
#         self.driver.get("https://www.google.com")
#         self.item_count = 0
#         self.max_items = 1000  # Set a high limit or None if you want all items

#     def parse(self, response):
#         print("Scraping started...")
#         self.driver.get(response.url)

#         # Initial wait for products to load
#         WebDriverWait(self.driver, 20).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, ".products.list.items.product-items"))
#         )

#         last_height = self.driver.execute_script("return document.body.scrollHeight")
#         load_more_attempts = 0
#         max_attempts = 5  # Maximum attempts to find/click load more button

#         while load_more_attempts < max_attempts:
#             try:
#                 # Scroll to bottom to ensure load more button is in view
#                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(2)  # Wait for any lazy loading

#                 # Try to find and click "Load More" button
#                 load_more_button = WebDriverWait(self.driver, 10).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, "a.action.more"))
#                 )
                
#                 if load_more_button.is_displayed():
#                     # Scroll the button into view and click using JavaScript
#                     self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
#                     time.sleep(1)
#                     self.driver.execute_script("arguments[0].click();", load_more_button)
                    
#                     # Wait for new content to load
#                     WebDriverWait(self.driver, 15).until(
#                         lambda driver: driver.execute_script("return document.body.scrollHeight") > last_height
#                     )
#                     last_height = self.driver.execute_script("return document.body.scrollHeight")
#                     load_more_attempts = 0  # Reset attempts counter after successful load
#                     print("Loaded more products...")
#                 else:
#                     load_more_attempts += 1
#                     print(f"Load more button not visible (attempt {load_more_attempts}/{max_attempts})")
                
#             except Exception as e:
#                 load_more_attempts += 1
#                 print(f"Error clicking load more (attempt {load_more_attempts}/{max_attempts}): {str(e)}")
#                 time.sleep(3)  # Wait before retrying

#         print("Finished loading all available products")

#         # Now scrape all loaded products
#         products = WebDriverWait(self.driver, 20).until(
#             EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'product-item')]"))
#         )
#         print(f"Total products found: {len(products)}")

#         for product in products:
#             if self.max_items and self.item_count >= self.max_items:
#                 break

#             try:
#                 name = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").text.strip() if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
                
#                 price_element = product.find_element(By.CSS_SELECTOR, 'span.price-wrapper span.price') if product.find_elements(By.CSS_SELECTOR, 'span.price-wrapper span.price') else None
#                 price = price_element.text.strip() if price_element else None
                
#                 product_url = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").get_attribute("href") if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
                
#                 image_element = product.find_element(By.CSS_SELECTOR, "img.product-image-photo")
#                 image_url = image_element.get_attribute("src") or image_element.get_attribute("data-src") if image_element else None

#                 if price:
#                     try:
#                         price_cleaned = price.replace("Rs.", "").replace("Rs", "").replace(",", "").strip()
#                         price = float(price_cleaned)
#                     except ValueError:
#                         price = None

#                 yield {
#                     'name': name,
#                     'price': price,
#                     'url': response.urljoin(product_url) if product_url else None,
#                     'image_url': image_url,
#                     'platform': "Shophive",
#                     'category': "Electronics"
#                 }

#                 self.item_count += 1
#             except Exception as e:
#                 print(f"Error processing product: {str(e)}")
#                 continue

#     def closed(self, reason):
#         self.driver.quit()
#         print(f"Spider closed because: {reason}")