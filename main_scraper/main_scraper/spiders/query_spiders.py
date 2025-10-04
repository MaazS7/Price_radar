import scrapy 
from urllib.parse import quote
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class DarazScraper(scrapy.Spider):
    name = "daraz_query"
    allowed_domains = ['daraz.pk']

    def __init__(self, query = '', *args ,**kwargs):
        super(DarazScraper, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://www.daraz.pk/catalog/?q={quote(query)}']

        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome()  
        self.driver.get("https://www.google.com")
        self.item_count = 0  

    def _parse(self, response, **kwargs):

        self.driver.get(response.url)


        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.Bm3ON")))
        
        html = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        products = response.css('div.Bm3ON') 

        for product in products:

            if self.item_count > 10:        #this line of code will make sure that only 10 items will scrap from website
                break


            name = product.css('div.RfADt a::text').get()
            price = product.css('span.ooOxS::text').get()
            product_url = product.css('a::attr(href)').get()
            image_url = product.css('img::attr(src)').get()


            yield {
                'name': name.strip() if name else None,
                'price': float(price.replace('Rs. ', '').replace(',', '')) if price else None,
                'url': response.urljoin(product_url) if product_url else None,
                'image_url': image_url if image_url else None,
                'platform' : "Daraz",
                'category': "Electronics"
            }

            self.item_count += 1  

        self.driver.quit()


class ShophiveSpider(scrapy.Spider):
    name = 'shophive_query'
    allowed_domains = ['shophive.com']
    
    def __init__(self, query='', *args, **kwargs):
        super(ShophiveSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://www.shophive.com/catalogsearch/result/?q={quote(query)}']
        
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome()  
        self.driver.get("https://www.google.com")
        self.item_count = 0  

    def parse(self, response):

        print("Scraping started...")
        self.driver.get(response.url)
        
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'product-item')]")))
        
        html = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        products = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'product-item')]") 
        
        for product in products:
            if self.item_count >= 5:  
                break

            name = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").text.strip() if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
            price_element = product.find_element(By.CSS_SELECTOR, 'span.price-wrapper span.price') if product.find_elements(By.CSS_SELECTOR, 'span.price-wrapper span.price') else None
            price = price_element.text.strip() if price_element else None
            product_url = product.find_element(By.CSS_SELECTOR, "h2.product-item-name a").get_attribute("href") if product.find_elements(By.CSS_SELECTOR, "h2.product-item-name a") else None
            image_url = product.find_element(By.CSS_SELECTOR, "img.product-image-photo").get_attribute("src") if product.find_elements(By.CSS_SELECTOR, "img.product-image-photo") else None

            
            if price:
                try:
                    price_cleaned = price.replace("Rs.", "").replace("Rs", "").replace(",", "").strip()
                    price = float(price_cleaned)
                except ValueError:
                    price = None

            yield {
                'name': name,
                'price': price,
                'url': response.urljoin(product_url) if product_url else None,
                'image_url': image_url,
                'platform' : "Shophive",
                'category': "Electronics"
            }

            self.item_count += 1  

    def closed(self):
        self.driver.quit()


class PriceOyeSpider(scrapy.Spider):
    name = 'priceoye_query'
    allowed_domains = ['priceoye.pk']
    
    def __init__(self, query='', *args, **kwargs):
        super(PriceOyeSpider, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://priceoye.pk/search?q={quote(query)}']
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome() 
        self.driver.get("https://www.google.com") 
        self.item_count = 0  

        

    def parse(self, response):

        print("Scraping started...")
        self.driver.get(response.url)
        
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.productBox.b-productBox")))

        html = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

        products = response.css('div.productBox.b-productBox')  
        
        for product in products:
            if self.item_count >= 3:  
                break

            name = product.css('div.p-title.bold.h5::text').get()
            price = response.css('div.price-box.p1 *::text').get()
            if price:
                price = price.replace('Rs', '').replace(',', '').strip()  
                price = float(price) if price else None  
            else:
                price = None  


            product_url = product.css('a[href*="/mobiles/"]::attr(href)').get()
            image_url = product.css('div.image-box amp-img::attr(src)').get()

            if not product:
                product_url = "www.priceoye.pk"
        
            yield {
                'name': name.strip() if name else None,
                'price': float(price.replace('Rs ', '').replace(',', '')) if price and price.replace('Rs ', '').strip() else None,
                'url': response.urljoin(product_url) if product_url else None,
                'image_url': image_url if image_url else None,
                'platform' : "PriceOye",
                'category': "Electronics"
            }

            self.item_count += 1  

        self.driver.quit()