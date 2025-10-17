# import scrapy
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from scrapy.http import HtmlResponse
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# import time, random
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
# # from pymongo import UpdateOne
# # from pymongo.errors import DuplicateKeyError

# class DarazScraper(scrapy.Spider):
#     name = "daraz_category"
#     allowed_domains = ['daraz.pk']

#     def __init__(self, *args, **kwargs):
#         super(DarazScraper, self).__init__(*args, **kwargs)
#         self.start_urls = [f'https://www.daraz.pk/catalog/?spm=a2a0e.searchlist.cate_2.9.1a2e762fRU9g5n&q=Televisions&from=hp_categories&src=all_channel']

#         chrome_options = Options()
#         # chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--window-size=1680,1050")
#         chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

#         service = Service()
#         self.driver = webdriver.Chrome(service=service, options=chrome_options)
#         self.driver.get(self.start_urls[0])

#     def scroll_and_load_images(self):
#         """Scroll through the page to trigger image loading"""
#         last_height = self.driver.execute_script("return document.body.scrollHeight")
#         scroll_pause = random.uniform(0.5, 1.5)
        
#         # Scroll down gradually
#         for i in range(0, last_height, 300):
#             self.driver.execute_script(f"window.scrollTo(0, {i});")
#             time.sleep(scroll_pause)
        
#         # Final scroll to bottom
#         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)

#     def click_next_page(self):
#         """Robust method to handle next page click with overlapping elements"""
#         try:
#             # Wait for next button to be present
#             next_button = WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "li.ant-pagination-next button.ant-pagination-item-link"))
#             )
            
#             # Check if button is enabled (not on last page)
#             if "ant-pagination-disabled" in self.driver.find_element(By.CSS_SELECTOR, "li.ant-pagination-next").get_attribute("class"):
#                 self.logger.info("Reached last page")
#                 return False
            
#             # Try regular click first
#             try:
#                 next_button.click()
#                 self.logger.info("Clicked next page using regular click")
#                 return True
#             except ElementClickInterceptedException:
#                 # If intercepted, use JavaScript click
#                 self.driver.execute_script("arguments[0].click();", next_button)
#                 self.logger.info("Clicked next page using JavaScript (element was intercepted)")
#                 return True
#             except Exception as e:
#                 self.logger.warning(f"Click failed, trying JavaScript: {e}")
#                 self.driver.execute_script("arguments[0].click();", next_button)
#                 return True
                
#         except TimeoutException:
#             self.logger.info("Next page button not found - probably last page")
#             return False
#         except Exception as e:
#             self.logger.error(f"Error clicking next page: {e}")
#             return False

#     def parse(self, response):
#         page_count = 1
#         max_pages = 82  # Safety limit to prevent infinite loops
        
#         while page_count <= max_pages:
#             try:
#                 self.logger.info(f"Processing page {page_count}")
                
#                 # Scroll to load images
#                 self.scroll_and_load_images()
                
#                 # Wait for products container
#                 WebDriverWait(self.driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "div.Bm3ON"))
#                 )
#                 time.sleep(random.uniform(1, 2))
                
#                 # Get fresh page source after scrolling
#                 html = self.driver.page_source
#                 response = HtmlResponse(url=self.driver.current_url, body=html.encode('utf-8'), encoding='utf-8')
                
#                 # Process products
#                 products = response.css('div.Bm3ON')[:40]  # Limit to 40 products
                
#                 for product in products:
#                     try:
#                         name = product.css('div.RfADt a::text').get()
#                         price = product.css('span.ooOxS::text').get()
#                         product_url = product.css('a::attr(href)').get()
#                         image_url = product.css('img::attr(src)').get()
                        
#                         # Fallback for lazy-loaded images
#                         if not image_url or 'placeholder' in image_url:
#                             image_url = product.css('img::attr(data-src)').get()
                        
#                         if product_url:  # Only process if we have a URL
#                             item = {
#                                 'name': name.strip() if name else None,
#                                 'price': float(price.replace('Rs. ', '').replace(',', '')) if price else None,
#                                 'url': response.urljoin(product_url),
#                                 'image_url': image_url if image_url else None,
#                                 'platform': "Daraz",
#                                 'category': "Electronics_TVs",
#                                 'page_number': page_count,
#                                 'last_updated': time.time()
#                             }
                            
#                             yield item

#                     except Exception as e:
#                         self.logger.error(f"Error processing product: {e}")
#                         continue

#                 # Try to go to next page
#                 if not self.click_next_page():
#                     self.logger.info("No more pages available")
#                     break
                
#                 # Wait for next page to load
#                 time.sleep(random.uniform(3, 5))
#                 page_count += 1

#             except Exception as e:
#                 self.logger.error(f"Error during parsing page {page_count}: {e}")
#                 break

#         self.logger.info("Scraping completed, closing browser")
#         self.driver.quit()

#     def closed(self, reason):
#         """Ensure browser is closed even if spider crashes"""
#         try:
#             self.driver.quit()
#         except:
#             pass


# class ShophiveSpider(scrapy.Spider):
#     name = 'shophive_category'
#     allowed_domains = ['shophive.com']
    
#     def __init__(self, *args, **kwargs):
#         super(ShophiveSpider, self).__init__(*args, **kwargs)
#         self.start_urls = [f'https://www.shophive.com/mobile-phones?manufacturer=apple,nokia,oneplus,oppo,philips,realme,samsung,sony,infinix,mi,honor,tecno,vivo,nothing,sego,dcode,itel']
        
#         chrome_options = Options()
#         # chrome_options.add_argument("--headless=new")  
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--window-size=1680,1050")
#         chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

#         self.driver = webdriver.Chrome(options=chrome_options)  
#         self.driver.get("https://www.google.com")
#         self.item_count = 0
#         self.max_items = 10000

#     def smooth_scroll_to_bottom(self, scroll_pause_time=2, scroll_step=300):
#         """Scroll down gradually with smooth animation"""
#         last_height = self.driver.execute_script("return document.body.scrollHeight")
#         current_position = 0
        
#         while current_position < last_height:
#             # Scroll down gradually
#             current_position += scroll_step
#             self.driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}});")
#             time.sleep(0.3)  # Short pause between scroll steps
            
#             # Update the last height
#             new_height = self.driver.execute_script("return document.body.scrollHeight")
#             if new_height > last_height:
#                 last_height = new_height
            
#             # Small random delay to mimic human behavior
#             time.sleep(random.uniform(0.1, 0.2))

#     def is_load_more_available(self):
#         """Check if Load More button is available and visible"""
#         try:
#             selectors = [
#                 "a.action.more",
#                 "button.action.primary",
#                 ".load-more",
#                 "#load-more",
#                 ".action-more",
#                 "a[title='Load More']"
#             ]
            
#             for selector in selectors:
#                 try:
#                     load_more_button = WebDriverWait(self.driver, 3).until(
#                         EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#                     )
#                     if load_more_button.is_displayed():
#                         return True
#                 except:
#                     continue
#             return False
#         except:
#             return False

#     def click_load_more(self):
#         """Click the Load More button if available"""
#         try:
#             selectors = [
#                 "a.action.more",
#                 "button.action.primary",
#                 ".load-more",
#                 "#load-more",
#                 ".action-more",
#                 "a[title='Load More']"
#             ]
            
#             for selector in selectors:
#                 try:
#                     load_more_button = WebDriverWait(self.driver, 5).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
#                     )
                    
#                     if load_more_button and load_more_button.is_displayed():
#                         print(f"Found Load More button with selector: {selector}")
                        
#                         # Scroll to the button smoothly
#                         self.driver.execute_script(
#                             "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
#                             load_more_button
#                         )
#                         time.sleep(1)
                        
#                         # Click using JavaScript to avoid interception
#                         self.driver.execute_script("arguments[0].click();", load_more_button)
#                         print("Clicked Load More button")
                        
#                         # Wait for new content to load
#                         time.sleep(3)
#                         WebDriverWait(self.driver, 15).until(
#                             EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
#                         )
                        
#                         return True
#                 except:
#                     continue
                    
#         except Exception as e:
#             print(f"Error clicking Load More button: {str(e)}")
#             return False
        
#         return False

#     def scrape_products(self):
#         """Extract product data from the current page"""
#         print("Starting to scrape products...")
        
#         # Final smooth scroll to ensure all content is loaded
#         self.smooth_scroll_to_bottom()
#         time.sleep(2)

#         products_data = []
        
#         # Now scrape all loaded products
#         try:
#             products = WebDriverWait(self.driver, 20).until(
#                 EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'product-item')]"))
#             )
#             print(f"Total products found: {len(products)}")

#             for product in products:
#                 if self.max_items and self.item_count >= self.max_items:
#                     print(f"Reached maximum item limit: {self.max_items}")
#                     break

#                 try:
#                     # Scroll each product into view smoothly before scraping
#                     self.driver.execute_script(
#                         "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
#                         product
#                     )
#                     time.sleep(0.1)  # Small pause after scrolling to each product
                    
#                     name = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").text.strip() if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
                    
#                     price_element = product.find_element(By.CSS_SELECTOR, 'span.price-wrapper span.price') if product.find_elements(By.CSS_SELECTOR, 'span.price-wrapper span.price') else None
#                     price = price_element.text.strip() if price_element else None
                    
#                     product_url = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").get_attribute("href") if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
                    
#                     image_element = product.find_element(By.CSS_SELECTOR, "img.product-image-photo")
#                     image_url = image_element.get_attribute("src") or image_element.get_attribute("data-src") if image_element else None

#                     if price:
#                         try:
#                             price_cleaned = price.replace("Rs.", "").replace("Rs", "").replace(",", "").strip()
#                             price = float(price_cleaned)
#                         except ValueError:
#                             price = None

#                     product_data = {
#                         'name': name,
#                         'price': price,
#                         'url': product_url,
#                         'image_url': image_url,
#                         'platform': "Shophive",
#                         'category': "Electronics",
#                         'sub_category': "Mobile Phones"
#                     }
                    
#                     products_data.append(product_data)
#                     self.item_count += 1
                    
#                     if self.item_count % 50 == 0:
#                         print(f"Scraped {self.item_count} products so far...")
                        
#                 except Exception as e:
#                     print(f"Error processing product: {str(e)}")
#                     continue

#         except Exception as e:
#             print(f"Error finding products: {str(e)}")
#             # Try alternative selector
#             try:
#                 products = self.driver.find_elements(By.CSS_SELECTOR, ".product-item")
#                 print(f"Found {len(products)} products with alternative selector")
#             except:
#                 products = []
#                 print("No products found")

#         print(f"Scraping completed. Total products scraped: {self.item_count}")
#         return products_data

#     def parse(self, response):
#         print("Scraping started...")
#         self.driver.get(response.url)

#         # Initial wait for products to load
#         WebDriverWait(self.driver, 20).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, ".products.list.items.product-items"))
#         )

#         load_more_attempts = 0
#         max_attempts = 50  # High limit to ensure all content loads
#         no_load_more_count = 0
#         max_no_load_more = 3  # Break if no load more button found 3 times in a row

#         print("Starting to load products...")

#         while load_more_attempts < max_attempts:
#             # Scroll to load any lazy-loaded content
#             self.smooth_scroll_to_bottom()
#             time.sleep(2)
            
#             # Check if load more button is available
#             if self.is_load_more_available():
#                 print("Load More button is available, attempting to click...")
#                 if self.click_load_more():
#                     print(f"Successfully loaded more products (attempt {load_more_attempts + 1})")
#                     load_more_attempts += 1
#                     no_load_more_count = 0  # Reset counter
                    
#                     # Scroll again after loading new content
#                     self.smooth_scroll_to_bottom(scroll_step=200)
#                     time.sleep(2)
#                 else:
#                     no_load_more_count += 1
#                     print(f"Failed to click Load More button (failures: {no_load_more_count})")
                    
#                     # If we can't click the button multiple times, break and scrape what we have
#                     if no_load_more_count >= 2:
#                         print("Cannot click Load More button - proceeding to scrape available products")
#                         break
#             else:
#                 no_load_more_count += 1
#                 print(f"No Load More button found (consecutive: {no_load_more_count})")
                
#                 # If no load more button found multiple times, break the loop and SCRAPE
#                 if no_load_more_count >= max_no_load_more:
#                     print("Load More button disappeared - all products loaded, starting to scrape...")
#                     break
            
#             # Small delay between attempts
#             time.sleep(2)

#             # Safety break if we've tried many times
#             if load_more_attempts >= max_attempts:
#                 print("Reached maximum load more attempts, proceeding to scrape...")
#                 break

#         print("Finished loading all available products")
        
#         # NOW SCRAPE THE PRODUCTS after pagination is complete
#         products_data = self.scrape_products()
        
#         # Yield all scraped products
#         for product in products_data:
#             yield product

#         print(f"Scraping completed. Total products scraped: {self.item_count}")

#     def closed(self, reason):
#         self.driver.quit()
#         print(f"Spider closed because: {reason}")

# from scrapy import Request

# class PriceOyeSpider(scrapy.Spider):
#     name = 'priceoye_category'
#     allowed_domains = ['priceoye.pk']
    
#     def __init__(self, *args, **kwargs):
#         super(PriceOyeSpider, self).__init__(*args, **kwargs)
#         self.start_urls = ['https://priceoye.pk/mobiles/pricelist?brands=samsung_infinix_oppo_xiaomi_vivo_tecno_realme']
        
#         chrome_options = Options()
#         # chrome_options.add_argument("--headless")  
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1680,1050")
#         chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

#         self.driver = webdriver.Chrome(options=chrome_options)
#         self.item_count = 0
#         self.current_page = 1
#         self.max_pages = 100  # Safety limit

#     def start_requests(self):
#         for url in self.start_urls:
#             yield Request(url, callback=self.parse)

#     def parse(self, response):
#         # Initial page load
#         self.driver.get(response.url)
#         time.sleep(3)  # Initial wait for page load
        
#         while self.current_page <= self.max_pages:
#             print(f"Scraping page {self.current_page}...")
            
#             # Wait for products to load with better error handling
#             try:
#                 WebDriverWait(self.driver, 30).until(
#                     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.productBox.b-productBox"))
#                 )
                
#                 # Multiple scrolls to ensure all products load
#                 last_height = self.driver.execute_script("return document.body.scrollHeight")
#                 for _ in range(3):
#                     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                     time.sleep(1)
#                     new_height = self.driver.execute_script("return document.body.scrollHeight")
#                     if new_height == last_height:
#                         break
#                     last_height = new_height
                
#                 # Scroll back to top to ensure all elements are in view
#                 self.driver.execute_script("window.scrollTo(0, 0);")
#                 time.sleep(1)
                
#             except Exception as e:
#                 self.logger.error(f"Error waiting for products on page {self.current_page}: {e}")
#                 break

#             # Parse the page content
#             html = self.driver.page_source
#             page_response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

#             # Extract products
#             products = page_response.css('div.productBox.b-productBox')  
            
#             if not products:
#                 print(f"No products found on page {self.current_page}. Stopping.")
#                 break
            
#             print(f"Found {len(products)} products on page {self.current_page}")
            
#             items_scraped_on_page = 0
#             for product in products:
#                 try:
#                     # Extract product name
#                     name = product.css('div.p-title.p-title-center.bold.h5::text').get()
#                     if not name:
#                         name = product.css('div.p-title::text').get()
                    
#                     if not name:
#                         continue  # Skip if no name found
                    
#                     name = name.strip()

#                     # Extract price
#                     price = product.css('div.price-box.p1 span::text').get()
#                     if price:
#                         price = price.replace('Rs', '').replace(',', '').strip()
#                         try:
#                             price = float(price) if price else None
#                         except ValueError:
#                             price = None
#                     else:
#                         price = None

#                     # Extract URLs
#                     product_url = product.css('a.ga-dataset::attr(href)').get()
#                     image_url = product.css('img.product-thumbnail-img::attr(src)').get()

#                     if product_url and not product_url.startswith('http'):
#                         product_url = response.urljoin(product_url)

#                     yield {
#                         'name': name,
#                         'price': price,
#                         'url': product_url,
#                         'image_url': image_url,
#                         'platform': "PriceOye",
#                         'category': "Electronics",
#                         'page_number': self.current_page
#                     }

#                     self.item_count += 1
#                     items_scraped_on_page += 1
#                     print(f"Scraped item {self.item_count}: {name}")

#                 except Exception as e:
#                     print(f"Error extracting product data: {e}")
#                     continue

#             print(f"Completed page {self.current_page}. Items scraped on this page: {items_scraped_on_page}, Total items: {self.item_count}")

#             # Check if we should stop (no products scraped)
#             if items_scraped_on_page == 0:
#                 print("No items scraped on current page. Stopping.")
#                 break

#             # PAGINATION - Try to go to next page
#             try:
#                 # Wait for pagination to be available
#                 WebDriverWait(self.driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pagination'))
#                 )
                
#                 # Find next button
#                 next_button = self.driver.find_element(By.CSS_SELECTOR, 'a#next-button.next[rel="next"]')
                
#                 # Check if next button is enabled
#                 if next_button.is_enabled() and 'disabled' not in next_button.get_attribute('class'):
#                     print("Clicking next button...")
                    
#                     # Store current URL to verify page change
#                     current_url = self.driver.current_url
                    
#                     # Scroll to next button and click using JavaScript
#                     self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
#                     time.sleep(1)
                    
#                     self.driver.execute_script("arguments[0].click();", next_button)
                    
#                     # Wait for page to change and load
#                     try:
#                         WebDriverWait(self.driver, 30).until(
#                             lambda driver: driver.current_url != current_url
#                         )
                        
#                         # Wait for products to load on new page
#                         WebDriverWait(self.driver, 30).until(
#                             EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.productBox.b-productBox"))
#                         )
                        
#                         self.current_page += 1
#                         print(f"Successfully moved to page {self.current_page}")
                        
#                         # Add a small delay before processing next page
#                         time.sleep(2)
                        
#                     except TimeoutException:
#                         print("Page did not change after clicking next button. Stopping.")
#                         break
                    
#                 else:
#                     print("Next button is disabled - no more pages available")
#                     break
                    
#             except TimeoutException:
#                 print("Pagination container not found within timeout. Stopping.")
#                 break
#             except NoSuchElementException:
#                 print("Next button element not found. Stopping.")
#                 break
#             except Exception as e:
#                 print(f"Error navigating to next page: {e}")
#                 break

#         print(f"Scraping completed. Total pages: {self.current_page - 1}, Total items: {self.item_count}")
#         self.driver.quit()

#     def closed(self, reason):
#         print(f"Spider closed: {reason}")
#         try:
#             self.driver.quit()
#         except:
#             pass