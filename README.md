🛒 Price Radar (Your Smart eShopping Partner)
A powerful multi-platform web scraping solution built with Scrapy to track product prices, monitor sales trends, and analyze ratings across multiple e-commerce websites.

🚀 Overview
This project automates the process of collecting product data from various e-commerce platforms, storing it in MongoDB Atlas, and providing insights through a Streamlit dashboard. The system tracks price changes, identifies sale patterns, and monitors product ratings to help users make informed purchasing decisions across different online retailers.

✨ Features
🔍 Multi-Platform Web Scraping
- Real-time data extraction using Scrapy framework across multiple sites

- Dynamic content handling with support for product badges and promotions

- Paginated crawling across multiple product categories

- Smart sale detection through platform-specific badge identification

- Ratings extraction for product quality assessment

- Platform-agnostic architecture for easy addition of new e-commerce sites

📊 Data Management
- MongoDB Atlas integration for scalable data storage

- Intelligent update logic for price tracking:

- Updates prices only when sale status changes

- Preserves historical price data

- Tracks sale status transitions

- Automatic schema evolution for new data fields

- Cross-platform data normalization

📈 Analytics Dashboard
- Interactive Streamlit dashboard for data visualization

- Price trend analysis over time

- Sale pattern detection

- Product ratings monitoring

- Category-wise performance metrics

- Platform comparison tools

🛠️ Technology Stack
Component	Technology
Web Scraping:	Python, Scrapy
Data Storage:	MongoDB Atlas
Analytics:	Streamlit, Pandas, Plotly
Language	Python 3.9+
Deployment:	Docker, GitHub Actions
Scheduling:	Apache Airflow (optional)

🏗️ Architecture
text
Multiple E-Commerce Sites → Scrapy Spiders → MongoDB Atlas → Streamlit Dashboard
         ↓                        ↓               ↓                ↓
    Amazon, Daraz,           Extracted      Persistent       User Insights
    Flipkart, etc.           Data           Storage
                           (Products,
                            Prices,
                            Ratings)
📦 Installation
Prerequisites
Python 3.9+

MongoDB Atlas account

Docker (optional)

Local Setup
bash
# Clone the repository
git clone https://github.com/yourusername/ecommerce-price-tracker.git
cd ecommerce-price-tracker

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your MongoDB credentials and platform-specific configurations

# Run the scraper for a specific platform
scrapy crawl daraz_spider 
scrapy crawl Mega_spider

# Run the container
docker run -d -p 8501:8501 --env-file .env ecommerce-tracker
🔧 Configuration
MongoDB Schema
javascript
{
  "url": "https://www.platform.com/product/...",
  "name": "Product Name",
  "current_price": 21499,
  "previous_price": 24999,
  "sale": false,
  "rating": 4.5,
  "rating_count": "526",
  "category": "Electronics",
  "sub_category": "Smartphones",
  "platform": "Daraz",
  "last_updated": "2024-01-15T10:30:00Z",
  "platform_specific_data": {
    "badge_type": "sale",
    "discount_percentage": 15,
    "prime_eligible": true
  }
}
Scraper Settings
python
# settings.py
BOT_NAME = 'ecommerce_scraper'
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1
USER_AGENT = 'Mozilla/5.0...'

# Platform-specific configurations
PLATFORM_CONFIGS = {
    'daraz': {
        'base_url': 'https://www.daraz.pk',
        'badge_selector': 'i.ic-dynamic-badge',
        'price_selector': 'span.ooOxS',
    },
    'amazon': {
        'base_url': 'https://www.amazon.com',
        'badge_selector': '.deal-badge',
        'price_selector': '.a-price-whole',
    }
}

🎯 Key Features Explained
Smart Price Tracking 🏷️
- Detects sale badges using platform-specific CSS selectors

- Updates prices only when sale status changes

- Maintains historical price data for trend analysis

- Cross-platform price comparison capabilities

Multi-Platform Support 🌐
Daraz: Detects sales through ic-dynamic-badge class

Amazon: Identifies deals and lightning deals

Flipkart: Detects festive sales and exchange offers

Custom platforms: Easily extendable architecture

Rating System ⭐
Extracts star ratings from product cards

Tracks total number of reviews

Monitors rating changes over time

Normalizes ratings across different platforms

Database Optimization 💾
Upsert operations for efficient updates

Conditional updates based on sale status

Schema flexibility for new data fields

Platform-specific data storage

📊 Dashboard Features
📈 Price Trends: Interactive line charts showing price history across platforms

🏷️ Sale Monitor: Real-time sale status tracking with platform filters

⭐ Rating Analytics: Distribution of product ratings with platform breakdown

📱 Category Analysis: Performance metrics by category and platform

🔍 Search & Filter: Advanced product search with cross-platform comparison

📊 Platform Comparison: Side-by-side price comparison across platforms

📉 Price Drop Alerts: Identify significant price drops across platforms

🚀 Adding New Platforms
Step 1: Create a New Spider
python
# spiders/new_platform_spider.py
import scrapy
from ..items import ProductItem

class NewPlatformSpider(scrapy.Spider):
    name = 'new_platform'
    allowed_domains = ['newplatform.com']
    
    def parse(self, response):
        # Implement platform-specific parsing logic
        pass
Step 2: Configure Platform Settings
python
# Update PLATFORM_CONFIGS in settings.py
PLATFORM_CONFIGS['new_platform'] = {
    'base_url': 'https://www.newplatform.com',
    'badge_selector': '.sale-badge',
    'price_selector': '.product-price',
    'rating_selector': '.rating-stars',
    'pagination_selector': '.next-page'
}
Step 3: Add Platform to Dashboard
python
# dashboard/config.py
PLATFORMS = ['daraz', 'amazon', 'PriceOye', 'new_platform']
🤝 Contributing
We welcome contributions! Here's how you can help:

Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

Areas We Need Help
🆕 Adding support for new e-commerce platforms

🐛 Bug fixes and performance improvements

📊 Dashboard enhancements

📝 Documentation improvements

🧪 Unit tests

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

👥 Authors
Maaz Shahzad

🙏 Acknowledgments
Scrapy for the powerful scraping framework

Streamlit for the amazing dashboard capabilities

MongoDB for reliable cloud data storage

All open-source contributors who made this possible


🌟 If you find this project useful, please consider giving it a star!

Made with ❤️ for the global e-commerce community
