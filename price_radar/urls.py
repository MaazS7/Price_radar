"""
URL configuration for price_radar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from scrapingApp.views import home_view
# from scrapingApp.views import loading_view
from scrapingApp.views import *
# from scrapingApp.views import get_scraped_data_view
# from scrapingApp.views import check_scraping_status



urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home_view ,name='home'),
    # path('loading/', loading_view, name='loading_view'),
    path('results/', search_product_view),
    path('search-product-view/', search_product_view, name='search-product-view'),
    path('getProductsBySearch/', getProductsBySearch, name='getProductsBySearch'),
    path('test/', test, name='test'),
    path('getProductsByCategory/', getProductsByCategory, name='getProductsByCategory'),
    path('getProductsBySubCategory/', getProductsBySubCategory, name='getProductsBySubCategory'),
    path('getProductsByPlatform/', getProductsByPlatform, name='getProductsBySubCategory'),
    path('sort_test/', sort_test, name='sort_test'),
    # path('search_products/', search_products, name='search_products')
    # path('startSchedular/', startSchedular, name='startSchedular'),
    # path('get-scraped-data/', get_scraped_data_view, name='get-scraped-data'),
    # path('check-scraping-status/', check_scraping_status)
]
