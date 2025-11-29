import scrapy
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time, random
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
# from pymongo import UpdateOne
# from pymongo.errors import DuplicateKeyError

class DarazScraper(scrapy.Spider):
    name = "daraz_category"
    allowed_domains = ['daraz.pk']

    def __init__(self, urls=None, *args, **kwargs):
        super(DarazScraper, self).__init__(*args, **kwargs)

        # Accept list or comma-separated URLs
        if urls:
            if isinstance(urls, str):
                self.urls_to_scrape = [u.strip() for u in urls.split(',') if u.strip()]
            else:
                self.urls_to_scrape = urls
        else:
            print("no urls found for scraping")
            self.urls_to_scrape = []

        # Initialize Chrome only once
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1680,1050")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def start_requests(self):
        """Start with ONLY the first URL in the list"""
        if not self.urls_to_scrape:
            self.logger.error("No URLs provided for scraping")
            return

        # Start with first URL only
        first_url = self.urls_to_scrape[0]
        remaining_urls = self.urls_to_scrape[1:]
        
        self.logger.info(f"🎯 Starting sequential scraping with {len(self.urls_to_scrape)} URLs")
        self.logger.info(f"📝 URLs to process: {self.urls_to_scrape}")
        
        # Detect category for first URL
        self._set_sub_category(first_url)
        
        yield scrapy.Request(
            url=first_url, 
            callback=self.parse_category, 
            meta={
                'current_url': first_url,
                'remaining_urls': remaining_urls,
                'current_url_index': 0
            }
        )

    def _set_sub_category(self, url):
        """Set sub_category based on URL content"""
        lower_url = url.lower()
        if "television" in lower_url:
            self.sub_category = "Televisions"
        elif "phone" in lower_url:
            self.sub_category = "Mobile Phones"
        elif "laptop" in lower_url:
            self.sub_category = "Laptops"
        elif "watches" in lower_url:
            self.sub_category = "Watches"
        elif "headsets" in lower_url or "headphone" in lower_url or "earbuds" in lower_url:
            self.sub_category = "Headphones"
        elif "appliances" in lower_url:
            self.sub_category = "Home Appliances"
        else:
            self.sub_category = "Other Electronics"
        self.logger.info(f"🏷️  Category detected: {self.sub_category}")

    def scroll_and_load_images(self):
        """Scroll through the page to trigger image loading"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_pause = random.uniform(0.5, 1.2)

        for i in range(0, last_height, 300):
            self.driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(scroll_pause)

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

    def click_next_page(self):
        """Click the 'next page' button."""
        try:
            next_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.ant-pagination-next button.ant-pagination-item-link"))
            )

            li_element = self.driver.find_element(By.CSS_SELECTOR, "li.ant-pagination-next")
            if "ant-pagination-disabled" in li_element.get_attribute("class"):
                return False

            try:
                next_button.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", next_button)

            return True

        except TimeoutException:
            return False
        except Exception:
            return False

    def parse_category(self, response):
        """Scrape each category (URL) fully before moving to the next."""
        current_url = response.meta['current_url']
        remaining_urls = response.meta['remaining_urls']
        current_url_index = response.meta['current_url_index']
        
        self.logger.info(f"🚀 Starting category {current_url_index + 1}/{len(self.urls_to_scrape)}: {current_url}")

        try:
            self.driver.get(current_url)
            time.sleep(3)
            page_count = 1
            max_pages = 103
            total_products_scraped = 0

            while page_count <= max_pages:
                self.logger.info(f"📄 Scraping page {page_count} of {current_url}")

                self.scroll_and_load_images()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.Bm3ON"))
                )

                html = self.driver.page_source
                page_response = HtmlResponse(url=self.driver.current_url, body=html.encode('utf-8'), encoding='utf-8')

                products = page_response.css('div.Bm3ON')
                if not products:
                    self.logger.info(f"❌ No products found on page {page_count} for {current_url}")
                    break

                page_products = 0
                for product in products:
                    try:
                        name = product.css('div.RfADt a::text').get()
                        price = product.css('span.ooOxS::text').get()
                        product_url = product.css('a::attr(href)').get()
                        is_on_sale = bool(product.css('i.ic-dynamic-badge').get())
                        image_url = product.css('img::attr(src)').get() or product.css('img::attr(data-src)').get()

                        rating_stars = product.css('div.mdmmT i._9-ogB.Dy1nx')  # Count filled stars
                        total_stars = len(rating_stars)  # This gives you the number of filled stars

                        rating_count = product.css('span.qzqFw::text').get()  # Returns "(526)"

                        if not product_url:
                            continue

                        item = {
                            'name': name.strip() if name else None,
                            'price': float(price.replace('Rs. ', '').replace(',', '')) if price else None,
                            'url': response.urljoin(product_url),
                            'image_url': image_url,
                            'platform': "Daraz",
                            'category': "Electronics",
                            'sub_category': self.sub_category,
                            'page_number': page_count,
                            'timestamp': time.time(),
                            'source_url': current_url,
                            'sale': is_on_sale,
                            'rating': total_stars,
                            'rating_count': rating_count
                        }

                        yield item
                        page_products += 1
                        total_products_scraped += 1

                    except Exception as e:
                        self.logger.error(f"Error extracting product: {e}")
                        continue

                self.logger.info(f"✅ Page {page_count} completed: {page_products} products scraped")

                # Check if there's a next page
                if not self.click_next_page():
                    self.logger.info(f"🎉 Category COMPLETED: {current_url} - Total: {total_products_scraped} products, {page_count} pages")
                    break

                page_count += 1
                time.sleep(random.uniform(2, 4))

            # After finishing current URL, move to next URL if any
            if remaining_urls:
                next_url = remaining_urls[0]
                next_remaining = remaining_urls[1:]
                next_index = current_url_index + 1
                
                self.logger.info(f"🔄 Moving to next URL: {next_url} ({next_index + 1}/{len(self.urls_to_scrape)})")
                
                # Detect category for next URL
                self._set_sub_category(next_url)
                
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_category,
                    meta={
                        'current_url': next_url,
                        'remaining_urls': next_remaining,
                        'current_url_index': next_index
                    }
                )
            else:
                self.logger.info("🎊 All URLs completed! Scraping finished.")

        except Exception as e:
            self.logger.error(f"❌ Error scraping {current_url}: {e}")
            
            # Even if error, try to move to next URL
            if remaining_urls:
                next_url = remaining_urls[0]
                self.logger.info(f"🔄 Error occurred, moving to next URL: {next_url}")
                
                self._set_sub_category(next_url)
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_category,
                    meta={
                        'current_url': next_url,
                        'remaining_urls': remaining_urls[1:],
                        'current_url_index': current_url_index + 1
                    }
                )

    def closed(self, reason):
        try:
            self.driver.quit()
        except:
            pass
        self.logger.info("🧹 Browser closed and spider finished.")


class ShophiveSpider(scrapy.Spider):
    name = 'shophive_category'
    allowed_domains = ['shophive.com']
    
    def __init__(self, urls=None, *args, **kwargs):
        super(ShophiveSpider, self).__init__(*args, **kwargs)
        
        # Accept list or comma-separated URLs
        if urls:
            if isinstance(urls, str):
                self.urls_to_scrape = [u.strip() for u in urls.split(',') if u.strip()]
            else:
                self.urls_to_scrape = urls
        else:
            # Default URL if none provided
            self.urls_to_scrape = ['https://www.shophive.com/mobile-phones?manufacturer=apple,nokia,oneplus,oppo,philips,realme,samsung,sony,infinix,mi,honor,tecno,vivo,nothing,sego,dcode,itel']

        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")  
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1680,1050")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)  
        self.driver.get("https://www.google.com")  # Initial page load
        self.item_count = 0
        self.max_items = 10000

    def _set_sub_category(self, url):
        
        lower_url = url.lower()
        if "television" in lower_url or "tv/led" in lower_url:
            self.sub_category = "Televisions"
        elif "phone" in lower_url or "mobile" in lower_url:
            self.sub_category = "Mobile Phones"
        elif "laptop" in lower_url:
            self.sub_category = "Laptops"
        elif "watches" in lower_url or "watch" in lower_url:
            self.sub_category = "Watches"
        elif "headsets" in lower_url or "headphone" in lower_url or "earbuds" in lower_url or "airpod" in lower_url:
            self.sub_category = "Headphones"
        elif "appliances" in lower_url:
            self.sub_category = "Home Appliances"
        else:
            self.sub_category = "Other Electronics"
        self.logger.info(f"🏷️  Category detected: {self.sub_category}")

    def start_requests(self):
        """Start with ONLY the first URL in the list"""
        if not self.urls_to_scrape:
            self.logger.error("No URLs provided for scraping")
            return

        # Start with first URL only
        first_url = self.urls_to_scrape[0]
        remaining_urls = self.urls_to_scrape[1:]
        
        self.logger.info(f"🎯 Starting sequential scraping with {len(self.urls_to_scrape)} URLs")
        self.logger.info(f"📝 URLs to process: {self.urls_to_scrape}")

        self._set_sub_category(first_url)
        
        yield scrapy.Request(
            url=first_url, 
            callback=self.parse, 
            meta={
                'current_url': first_url,
                'remaining_urls': remaining_urls,
                'current_url_index': 0
            }
        )

    def smooth_scroll_to_bottom(self, scroll_pause_time=2, scroll_step=300):
        """Scroll down gradually with smooth animation"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        
        while current_position < last_height:
            # Scroll down gradually
            current_position += scroll_step
            self.driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}});")
            time.sleep(0.3)  # Short pause between scroll steps
            
            # Update the last height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height > last_height:
                last_height = new_height
            
            # Small random delay to mimic human behavior
            time.sleep(random.uniform(0.1, 0.2))

    def is_load_more_available(self):
        """Check if Load More button is available and visible"""
        try:
            selectors = [
                "a.action.more",
                "button.action.primary",
                ".load-more",
                "#load-more",
                ".action-more",
                "a[title='Load More']"
            ]
            
            for selector in selectors:
                try:
                    load_more_button = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if load_more_button.is_displayed():
                        return True
                except:
                    continue
            return False
        except:
            return False

    def click_load_more(self):
        """Click the Load More button if available"""
        try:
            selectors = [
                "a.action.more",
                "button.action.primary",
                ".load-more",
                "#load-more",
                ".action-more",
                "a[title='Load More']"
            ]
            
            for selector in selectors:
                try:
                    load_more_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    if load_more_button and load_more_button.is_displayed():
                        print(f"Found Load More button with selector: {selector}")
                        
                        # Scroll to the button smoothly
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                            load_more_button
                        )
                        time.sleep(1)
                        
                        # Click using JavaScript to avoid interception
                        self.driver.execute_script("arguments[0].click();", load_more_button)
                        print("Clicked Load More button")
                        
                        # Wait for new content to load
                        time.sleep(3)
                        WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
                        )
                        
                        return True
                except:
                    continue
                    
        except Exception as e:
            print(f"Error clicking Load More button: {str(e)}")
            return False
        
        return False

    def scrape_products(self, current_url):
        """Extract product data from the current page"""
        print("Starting to scrape products...")
        
        # Final smooth scroll to ensure all content is loaded
        self.smooth_scroll_to_bottom()
        time.sleep(2)

        products_data = []
        
        # Now scrape all loaded products
        try:
            products = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'product-item')]"))
            )
            print(f"Total products found: {len(products)}")

            for product in products:
                if self.max_items and self.item_count >= self.max_items:
                    print(f"Reached maximum item limit: {self.max_items}")
                    break

                try:
                    # Scroll each product into view smoothly before scraping
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                        product
                    )
                    time.sleep(0.1)  # Small pause after scrolling to each product
                    
                    name = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").text.strip() if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
                    
                    price_element = product.find_element(By.CSS_SELECTOR, 'span.price-wrapper span.price') if product.find_elements(By.CSS_SELECTOR, 'span.price-wrapper span.price') else None
                    price = price_element.text.strip() if price_element else None
                    
                    product_url = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").get_attribute("href") if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
                    
                    image_element = product.find_element(By.CSS_SELECTOR, "img.product-image-photo")
                    image_url = image_element.get_attribute("src") or image_element.get_attribute("data-src") if image_element else None

                    if price:
                        try:
                            price_cleaned = price.replace("Rs.", "").replace("Rs", "").replace(",", "").strip()
                            price = float(price_cleaned)
                        except ValueError:
                            price = None

                    # Extract category from URL
                    # parts = current_url.replace("https://www.shophive.com/", "").split("?")[0].split("/")
                    # category = parts[0].replace("-", " ").title() if parts else "Electronics"
                    # sub_category = parts[1].replace("-", " ").title() if len(parts) > 1 else "Mobile Phones"

                    product_data = {
                        'name': name,
                        'price': price,
                        'url': product_url,
                        'image_url': image_url,
                        'platform': "Shophive",
                        'category': "Electronics",
                        'sub_category': self.sub_category,
                        'source_url': current_url,
                        'timestamp': time.time()
                    }
                    
                    products_data.append(product_data)
                    self.item_count += 1
                    
                    if self.item_count % 50 == 0:
                        print(f"Scraped {self.item_count} products so far...")
                        
                except Exception as e:
                    print(f"Error processing product: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error finding products: {str(e)}")
            # Try alternative selector
            try:
                products = self.driver.find_elements(By.CSS_SELECTOR, ".product-item")
                print(f"Found {len(products)} products with alternative selector")
            except:
                products = []
                print("No products found")

        print(f"Scraping completed. Total products scraped: {len(products_data)} from this URL")
        return products_data

    def parse(self, response):
        """Scrape each category (URL) fully before moving to the next."""
        current_url = response.meta['current_url']
        remaining_urls = response.meta['remaining_urls']
        current_url_index = response.meta['current_url_index']
        
        self.logger.info(f"🚀 Starting category {current_url_index + 1}/{len(self.urls_to_scrape)}: {current_url}")

        print("Scraping started...")
        self.driver.get(current_url)

        # Initial wait for products to load
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".products.list.items.product-items"))
        )

        load_more_attempts = 0
        max_attempts = 50  # High limit to ensure all content loads
        no_load_more_count = 0
        max_no_load_more = 3  # Break if no load more button found 3 times in a row

        print("Starting to load products...")

        while load_more_attempts < max_attempts:
            # Scroll to load any lazy-loaded content
            self.smooth_scroll_to_bottom()
            time.sleep(2)
            
            # Check if load more button is available
            if self.is_load_more_available():
                print("Load More button is available, attempting to click...")
                if self.click_load_more():
                    print(f"Successfully loaded more products (attempt {load_more_attempts + 1})")
                    load_more_attempts += 1
                    no_load_more_count = 0  # Reset counter
                    
                    # Scroll again after loading new content
                    self.smooth_scroll_to_bottom(scroll_step=200)
                    time.sleep(2)
                else:
                    no_load_more_count += 1
                    print(f"Failed to click Load More button (failures: {no_load_more_count})")
                    
                    # If we can't click the button multiple times, break and scrape what we have
                    if no_load_more_count >= 2:
                        print("Cannot click Load More button - proceeding to scrape available products")
                        break
            else:
                no_load_more_count += 1
                print(f"No Load More button found (consecutive: {no_load_more_count})")
                
                # If no load more button found multiple times, break the loop and SCRAPE
                if no_load_more_count >= max_no_load_more:
                    print("Load More button disappeared - all products loaded, starting to scrape...")
                    break
            
            # Small delay between attempts
            time.sleep(2)

            # Safety break if we've tried many times
            if load_more_attempts >= max_attempts:
                print("Reached maximum load more attempts, proceeding to scrape...")
                break

        print("Finished loading all available products")
        
        # NOW SCRAPE THE PRODUCTS after pagination is complete
        products_data = self.scrape_products(current_url)
        
        # Yield all scraped products
        for product in products_data:
            yield product

        category_item_count = len(products_data)
        print(f"✅ Category COMPLETED: {current_url} - Products: {category_item_count}")

        # After finishing current URL, move to next URL if any
        if remaining_urls:
            next_url = remaining_urls[0]
            next_remaining = remaining_urls[1:]
            next_index = current_url_index + 1
            
            self.logger.info(f"🔄 Moving to next URL: {next_url} ({next_index + 1}/{len(self.urls_to_scrape)})")

            self._set_sub_category(next_url)
            
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                meta={
                    'current_url': next_url,
                    'remaining_urls': next_remaining,
                    'current_url_index': next_index
                }
            )
        else:
            self.logger.info(f"🎊 All URLs completed! Total items scraped: {self.item_count}")

    def closed(self, reason):
        self.driver.quit()
        print(f"Spider closed because: {reason}")

# from scrapy import Request


class PriceOyeSpider(scrapy.Spider):
    name = 'priceoye_category'
    allowed_domains = ['priceoye.pk']

    def __init__(self, urls=None, *args, **kwargs):
        """
        Pass multiple URLs dynamically:
        e.g. process.crawl(PriceOyeSpider, urls=[
                'https://priceoye.pk/mobiles/pricelist?brands=samsung',
                'https://priceoye.pk/laptops/pricelist'
            ])
        """
        super(PriceOyeSpider, self).__init__(*args, **kwargs)
        
        # Accept list or comma-separated URLs
        if urls:
            if isinstance(urls, str):
                self.urls_to_scrape = [u.strip() for u in urls.split(',') if u.strip()]
            else:
                self.urls_to_scrape = urls
        else:
            self.urls_to_scrape = []

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1680,1050")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.max_pages = 100  # Safety limit
        self.item_limit = 10000  # Total items across all URLs
        self.item_count = 0

    def _set_sub_category(self, url):
        """Set sub_category based on URL content - SAME LOGIC AS DARAZ SPIDER"""
        lower_url = url.lower()
        if "television" in lower_url:
            self.sub_category = "Televisions"
        elif "phone" in lower_url or "mobile" in lower_url:
            self.sub_category = "Mobile Phones"
        elif "laptop" in lower_url:
            self.sub_category = "Laptops"
        elif "tablets" in lower_url:
            self.sub_category = "Tablets"
        elif "watches" in lower_url:
            self.sub_category = "Watches"
        elif "headsets" in lower_url or "headphone" in lower_url or "earbuds" in lower_url:
            self.sub_category = "Headphones"
        elif "appliances" in lower_url:
            self.sub_category = "Home Appliances"
        else:
            self.sub_category = "Other Electronics"
        self.logger.info(f"🏷️  Category detected: {self.sub_category}")

    def start_requests(self):
        """Start with ONLY the first URL in the list"""
        if not self.urls_to_scrape:
            self.logger.error("No URLs provided for scraping")
            return

        # Start with first URL only
        first_url = self.urls_to_scrape[0]
        remaining_urls = self.urls_to_scrape[1:]
        
        self.logger.info(f"🎯 Starting sequential scraping with {len(self.urls_to_scrape)} URLs")
        self.logger.info(f"📝 URLs to process: {self.urls_to_scrape}")

        self._set_sub_category(first_url)
        
        yield scrapy.Request(
            url=first_url, 
            callback=self.parse, 
            meta={
                'current_url': first_url,
                'remaining_urls': remaining_urls,
                'current_url_index': 0
            }
        )

    def parse(self, response):
        """Scrape each category (URL) fully before moving to the next."""
        current_url = response.meta['current_url']
        remaining_urls = response.meta['remaining_urls']
        current_url_index = response.meta['current_url_index']
        
        self.logger.info(f"🚀 Starting category {current_url_index + 1}/{len(self.urls_to_scrape)}: {current_url}")

        self.current_page = 1
        category_item_count = 0

        self.driver.get(current_url)
        time.sleep(3)

        while self.current_page <= self.max_pages:
            print(f"📄 Scraping page {self.current_page} for {current_url}")

            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div.productBox.b-productBox"))
                )

                # Scroll to load all products
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                self.driver.execute_script("window.scrollTo(0, 0);")

            except Exception as e:
                self.logger.error(f"Error waiting for products: {e}")
                break

            html = self.driver.page_source
            page_response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')
            products = page_response.css('div.productBox.b-productBox')

            if not products:
                print(f"No products found on page {self.current_page}. Ending this category.")
                break

            print(f"✅ Found {len(products)} products on page {self.current_page}")

            items_scraped_on_page = 0
            for product in products:
                if self.item_count >= self.item_limit:
                    print(f"Reached item limit ({self.item_limit}). Stopping spider.")
                    self.driver.quit()
                    return

                try:
                    # --- Product Name ---
                    name = product.css('div.p-title.p-title-center.bold.h5::text').get()
                    if not name:
                        name = product.css('div.p-title::text').get()
                    if not name:
                        continue
                    name = name.strip()

                    # --- Price ---
                    price = product.css('div.price-box.p1 span::text').get()
                    if price:
                        price = price.replace('Rs', '').replace(',', '').strip()
                        try:
                            price = float(price)
                        except ValueError:
                            price = None

                    # --- Product URL + Image ---
                    product_url = product.css('a.ga-dataset::attr(href)').get()
                    image_url = product.css('img.product-thumbnail-img::attr(src)').get()
                    on_sale = bool(product.css('i.ic-dynamic-badge img').get())
                    if product_url and not product_url.startswith('http'):
                        product_url = response.urljoin(product_url)
                    

                    yield {
                        'name': name,
                        'price': price,
                        'url': product_url,
                        'image_url': image_url,
                        'platform': "PriceOye",
                        'category': "Electronics",
                        'sub_category': self.sub_category,
                        'page_number': self.current_page,
                        'source_url': current_url,
                        'timestamp': time.time(),
                        'sale': on_sale
                    }

                    self.item_count += 1
                    category_item_count += 1
                    items_scraped_on_page += 1
                    print(f"🛒 Scraped item {self.item_count}: {name}")

                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue

            print(f"📊 Page {self.current_page} done: {items_scraped_on_page} items scraped")

            if items_scraped_on_page == 0:
                print("No items on this page. Stopping category.")
                break

            # --- Handle Pagination ---
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pagination'))
                )
                next_button = self.driver.find_element(By.CSS_SELECTOR, 'a#next-button.next[rel="next"]')

                if next_button.is_enabled() and 'disabled' not in next_button.get_attribute('class'):
                    print("➡️ Clicking next page...")
                    current_driver_url = self.driver.current_url
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", next_button)

                    WebDriverWait(self.driver, 30).until(
                        lambda driver: driver.current_url != current_driver_url
                    )
                    WebDriverWait(self.driver, 30).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "div.productBox.b-productBox"))
                    )

                    self.current_page += 1
                    print(f"✅ Moved to page {self.current_page}")
                    time.sleep(random.uniform(2, 4))

                else:
                    print("🚫 Next button disabled — no more pages.")
                    break

            except (TimeoutException, NoSuchElementException):
                print("⚠️ Pagination not found or stopped. Ending category.")
                break
            except Exception as e:
                print(f"Error moving to next page: {e}")
                break

        print(f"🏁 Completed {current_url} | Pages: {self.current_page - 1} | Category items: {category_item_count} | Total items: {self.item_count}")

        # After finishing current URL, move to next URL if any
        if remaining_urls:
            next_url = remaining_urls[0]
            next_remaining = remaining_urls[1:]
            next_index = current_url_index + 1
            
            self.logger.info(f"🔄 Moving to next URL: {next_url} ({next_index + 1}/{len(self.urls_to_scrape)})")

            self._set_sub_category(next_url)
            
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                meta={
                    'current_url': next_url,
                    'remaining_urls': next_remaining,
                    'current_url_index': next_index
                }
            )
        else:
            self.logger.info("🎊 All URLs completed! Scraping finished.")

    def closed(self, reason):
        print(f"Spider closed: {reason}")
        try:
            self.driver.quit()
        except:
            pass


class MegaScraper(scrapy.Spider):
    name = "mega_category"
    allowed_domains = ['mega.pk']

    def __init__(self, urls=None, *args, **kwargs):
        super(MegaScraper, self).__init__(*args, **kwargs)  

        # Accept list or comma-separated URLs
        if urls:
            if isinstance(urls, str):
                self.urls_to_scrape = [u.strip() for u in urls.split(',') if u.strip()]
            else:
                self.urls_to_scrape = urls
        else:
            print("no urls found for scraping")
            self.urls_to_scrape = []

        # Initialize Chrome only once
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1680,1050")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def start_requests(self):
        """Start with ONLY the first URL in the list"""
        if not self.urls_to_scrape:
            self.logger.error("No URLs provided for scraping")
            return

        # Start with first URL only
        first_url = self.urls_to_scrape[0]
        remaining_urls = self.urls_to_scrape[1:]
        
        self.logger.info(f"🎯 Starting sequential scraping with {len(self.urls_to_scrape)} URLs")
        self.logger.info(f"📝 URLs to process: {self.urls_to_scrape}")
        
        # Detect category for first URL
        self._set_sub_category(first_url)
        
        yield scrapy.Request(
            url=first_url, 
            callback=self.parse_category, 
            meta={
                'current_url': first_url,
                'remaining_urls': remaining_urls,
                'current_url_index': 0
            }
        )

    def _set_sub_category(self, url):
        """Set sub_category based on URL content"""
        lower_url = url.lower()
        if "television" in lower_url or "tv/led":
            self.sub_category = "Televisions"
        elif "phone" in lower_url or "mobiles" in lower_url:
            self.sub_category = "Mobile Phones"
        elif "laptop" in lower_url:
            self.sub_category = "Laptops"
        elif "watches" in lower_url:
            self.sub_category = "Watches"
        elif "headsets" in lower_url or "headphone" in lower_url or "earbuds" in lower_url:
            self.sub_category = "Headphones"
        elif "appliances" in lower_url:
            self.sub_category = "Home Appliances"
        elif "printer" in lower_url:
            self.sub_category = "Printers"
        else:
            self.sub_category = "Other Electronics"
        self.logger.info(f"🏷️  Category detected: {self.sub_category}")

    def scroll_and_load_images(self):
        """Scroll through the page to trigger image loading"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_pause = random.uniform(0.5, 1.2)

        for i in range(0, last_height, 300):
            self.driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(scroll_pause)

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

    def click_next_page(self):
        """Click the 'next page' button."""
        try:
            # Find the pagination div and get the last <a> tag which is the next button
            next_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.pagination a:last-child"))
            )
            
            # Check if the next button is not disabled (it's an <a> tag, not a disabled span)
            if next_button.get_attribute('href'):
                try:
                    next_button.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", next_button)
                
                return True
            else:
                return False

        except TimeoutException:
            return False
        except Exception as e:
            self.logger.error(f"Error clicking next page: {e}")
            return False

    def parse_category(self, response):
        """Scrape each category (URL) fully before moving to the next."""
        current_url = response.meta['current_url']
        remaining_urls = response.meta['remaining_urls']
        current_url_index = response.meta['current_url_index']
        
        self.logger.info(f"🚀 Starting category {current_url_index + 1}/{len(self.urls_to_scrape)}: {current_url}")

        try:
            self.driver.get(current_url)
            time.sleep(3)
            page_count = 1
            max_pages = 103
            total_products_scraped = 0

            while page_count <= max_pages:
                self.logger.info(f"📄 Scraping page {page_count} of {current_url}")

                self.scroll_and_load_images()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.cat-div.col-md-12"))
                )

                html = self.driver.page_source
                page_response = HtmlResponse(url=self.driver.current_url, body=html.encode('utf-8'), encoding='utf-8')

                # Get all product boxes
                products = page_response.css('li.col-xs-6.col-sm-4.col-md-4.col-lg-3')

                if not products:
                    self.logger.info(f"❌ No products found on page {page_count} for {current_url}")
                    break

                self.logger.info(f"Found {len(products)} products on page {page_count}")

                page_products = 0
                for product in products:
                    try:
                        # Fixed selectors based on actual HTML structure
                        name = product.css('#lap_name_div h3 a::text').get()
                        price = product.css('div.cat_price::text').getall()
                        if price:
                            # Filter out whitespace and get the actual price (not the .was price)
                            price = [p.strip() for p in price if p.strip()][-1]
                        product_url = product.css('#lap_name_div h3 a::attr(href)').get()
                        image_url = product.css('.image .wrapper1 img::attr(src)').get()
                        
                        # Get specs if they exist
                        specs = []
                        spec_elements = product.css('.detailer li::text')
                        for spec in spec_elements:
                            spec_text = spec.get()
                            if spec_text and spec_text.strip():
                                specs.append(spec_text.strip(' -'))

                        if not product_url or not name:
                            self.logger.warning(f"Skipping product - missing URL or name")
                            continue

                        # Clean price
                        price_value = None
                        if price:
                            try:
                                price_value = float(price.replace('Rs. ', '').replace(',', '').strip())
                            except (ValueError, AttributeError) as e:
                                self.logger.warning(f"Could not parse price: {price} - {e}")

                        item = {
                            'name': name.strip(),
                            'price': price_value,
                            'url': response.urljoin(product_url),
                            'image_url': image_url,
                            'platform': "Mega",
                            'category': "Electronics",
                            'sub_category': self.sub_category,
                            'page_number': page_count,
                            'timestamp': time.time(),
                            'source_url': current_url,
                            'specifications': specs
                        }

                        yield item
                        page_products += 1
                        total_products_scraped += 1

                    except Exception as e:
                        self.logger.error(f"Error extracting product: {e}")
                        continue

                self.logger.info(f"✅ Page {page_count} completed: {page_products} products scraped")

                # Check if there's a next page
                if not self.click_next_page():
                    self.logger.info(f"🎉 Category COMPLETED: {current_url} - Total: {total_products_scraped} products, {page_count} pages")
                    break

                page_count += 1
                time.sleep(random.uniform(2, 4))

            # After finishing current URL, move to next URL if any
            if remaining_urls:
                next_url = remaining_urls[0]
                next_remaining = remaining_urls[1:]
                next_index = current_url_index + 1
                
                self.logger.info(f"🔄 Moving to next URL: {next_url} ({next_index + 1}/{len(self.urls_to_scrape)})")
                
                # Detect category for next URL
                self._set_sub_category(next_url)
                
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_category,
                    meta={
                        'current_url': next_url,
                        'remaining_urls': next_remaining,
                        'current_url_index': next_index
                    }
                )
            else:
                self.logger.info("🎊 All URLs completed! Scraping finished.")

        except Exception as e:
            self.logger.error(f"❌ Error scraping {current_url}: {e}")
            
            # Even if error, try to move to next URL
            if remaining_urls:
                next_url = remaining_urls[0]
                self.logger.info(f"🔄 Error occurred, moving to next URL: {next_url}")
                
                self._set_sub_category(next_url)
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_category,
                    meta={
                        'current_url': next_url,
                        'remaining_urls': remaining_urls[1:],
                        'current_url_index': current_url_index + 1
                    }
                )

    def closed(self, reason):
        try:
            self.driver.quit()
        except:
            pass
        self.logger.info("🧹 Browser closed and spider finished.")

