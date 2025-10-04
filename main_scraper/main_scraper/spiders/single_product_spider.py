import scrapy
from playwright.async_api import async_playwright

class DarazPlaywrightSpider(scrapy.Spider):
    name = "daraz_single_product"
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,  # Faster in headless mode
            "timeout": 15000
        },
        "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
        "PLAYWRIGHT_MAX_CONTEXTS": 5,  # Limit concurrent contexts
        "CONCURRENT_REQUESTS": 5,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 15000,
        "DOWNLOAD_TIMEOUT": 20,
        "PLAYWRIGHT_BLOCK_RESOURCE_TYPES": [  # Block unnecessary resources
            "image", 
            "stylesheet", 
            "font",
            "media"
        ],
    }

    def __init__(self, query='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        # URLs should be passed as a comma-separated string
        self.urls = [url.strip() for url in query.split(',') if url.strip() and url.startswith(('http://', 'https://'))]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True, 
                    "playwright_include_page": True,
                    "playwright_page_goto_kwargs": {
                        "timeout": 20000,  # 10 seconds timeout
                        "wait_until": "domcontentloaded"  # Fastest option
                    },
                    "playwright_context": "default",
                    "playwright_context_kwargs": {
                        "ignore_https_errors": True,
                    }
                },
                callback=self.parse,
                errback=self.errback
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        
        try:
            # Wait for and extract price directly using Playwright (fastest method)
            price_element = await page.wait_for_selector("span.pdp-price.pdp-price_type_normal", timeout=8000)
            price_text = await price_element.text_content()
            
            # Clean up immediately
            await page.close()

            yield {
                'url': response.url,
                'price': float(price_text.replace('Rs.', '').replace(',', '').strip()) if price_text else None,
            }

        except Exception as e:
            await page.close()
            self.logger.error(f"Error scraping {response.url}: {e}")
            # Optionally yield a result with error info
            yield {
                'url': response.url,
                'price': None,
                'error': str(e)
            }

    async def errback(self, failure):
        """Handle request errors"""
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        
        self.logger.error(f"Request failed: {failure.value}")
        
        # Yield error result
        yield {
            'url': failure.request.url,
            'price': None,
            'platform': 'Daraz',
            'error': str(failure.value)
        }


class ShophivePlaywrightSpider(scrapy.Spider):
    name = "shophive_single_product"
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,  # Faster in headless mode
            "timeout": 15000
        },
        "CONCURRENT_REQUESTS": 5,  # Reduced for stability
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 15000,
        "DOWNLOAD_TIMEOUT": 20,
        "PLAYWRIGHT_BLOCK_RESOURCE_TYPES": [  # Block unnecessary resources
            "image", 
            "stylesheet", 
            "font",
            "media"
        ],
    }

    def __init__(self, query='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        # URLs should be passed as a comma-separated string
        self.urls = [url.strip() for url in query.split(',') if url.strip() and url.startswith(('http://', 'https://'))]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True, 
                    "playwright_include_page": True,
                    "playwright_page_goto_kwargs": {
                        "timeout": 10000,  # 10 seconds timeout
                        "wait_until": "domcontentloaded"  # Fastest option
                    },
                    "playwright_context_kwargs": {
                        "ignore_https_errors": True,
                    }
                },
                callback=self.parse,
                errback=self.errback
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        
        try:
            # Wait for and extract price directly using Playwright (fastest method)
            price_element = await page.wait_for_selector("span.pdp-price.pdp-price_type_normal", timeout=8000)
            price_text = await price_element.text_content()
            
            # Clean up immediately
            await page.close()

            yield {
                'url': response.url,
                'price': float(price_text.replace('Rs.', '').replace(',', '').strip()) if price_text else None,
            }

        except Exception as e:
            await page.close()
            self.logger.error(f"Error scraping {response.url}: {e}")
            # Optionally yield a result with error info
            yield {
                'url': response.url,
                'price': None,
                'error': str(e)
            }

    async def errback(self, failure):
        """Handle request errors"""
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        
        self.logger.error(f"Request failed: {failure.value}")
        
        # Yield error result
        yield {
            'url': failure.request.url,
            'price': None,
            'platform': 'Daraz',
            'error': str(failure.value)
        }



# class ShophiveScraper(scrapy.Spider):
#     name = "shophive"
#     allowed_domains = ['shophive.com']

#     def __init__(self, url = '', *args ,**kwargs):
#         super(ShophiveScraper, self).__init__(*args, **kwargs)
#         self.start_urls = [f'{url}']

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

#     def _parse(self, response, **kwargs):

#         self.driver.get(response.url)

#         # Wait for either the price or title to be present
#         WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.special-price span.price")))

#         # Capture and parse the full HTML
#         html = self.driver.page_source
#         response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')

#         # Extract the price text
#         price = response.css("span.special-price span.price::text").get()

#         yield {
#             'price': float(price.replace('Rs. ', '').replace(',', '')) if price else None,
#         }

#         self.driver.quit()


