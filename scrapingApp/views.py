from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
# import subprocess
from subprocess import Popen
from subprocess import Popen
from datetime import datetime
import os
import re
from django.http import JsonResponse, HttpResponse
# from django.conf import settings
from datetime import datetime, timedelta, timezone
import requests
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse



import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



# Connect to MongoDB Atlas
Client = MongoClient("mongodb+srv://priceradarpk:priceradar@priceradar.b6bkx.mongodb.net/?retryWrites=true&w=majority&appName=PriceRadar")
Db = Client["priceradar"]
products_collection = Db["products"]



def home_view(request):
    return render(request, "home.html")

# def updateRecords(request):
#     try:
#         result = products_collection.update_many(
#             {"platform": {"$regex": "^PriceOye$", "$options": "i"} and "": {"$regex": "^PriceOye$", "$options": "i"}},
#             {"$set": {"sub_category": "Mobile Phones"}}
#         )
#         return HttpResponse(f"Updated successfully. Modified {result.modified_count} documents.")
#     except Exception as e:
#         return HttpResponse(f"Update failed: {e}", status=500)




def search_product_view(request):
    print("🔎 Search product function started")

    query = request.GET.get("query", "").strip()
    if not query:
        return render(request, "home.html", {"error": "Please enter a valid query."})

    if "scraping_query" in request.session:
        del request.session["scraping_query"]
    if "scraping_started" in request.session:
        del request.session["scraping_started"]

    products = search_products(query)

    if products:
        hours_threshold = 24
        time_limit = datetime.now(timezone.utc) - timedelta(hours=hours_threshold)

        stale_products_urls = [
            product.get("url") for product in products
            if product.get("last_updated") and
            product["last_updated"].astimezone(timezone.utc) < time_limit
        ]
        if len(stale_products_urls) > 0:
            product_updation(stale_products_urls)

            return HttpResponse("Products updating in progress")

        else:
            data = [{'title': prod.get("name"), 'original_price': prod.get("original_price"), 'current_price': prod.get("current_price"), 'previous_price': prod.get("previous_price"), 'category': prod.get("category"),'url': prod.get("url"), 'image_url': prod.get("image_url"), 'platform': prod.get("platform")} for prod in products]
            # return render(request, "results.html", {'products': products})
            return JsonResponse(data, safe=False)
    else:
    
        try:
            request.session["scraping_query"] = query
            request.session["scraping_started"] = datetime.now().isoformat()
            request.session.modified = True
            
            print("Starting scraper process...")
            
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            manage_py_path = os.path.join(project_root, 'manage.py')
        
            print(f"Project root: {project_root}")  # checking if it getting to project root directory 'price_radar' or not 
            print(f"Manage.py path: {manage_py_path}")  # Should show full path to manage.py
        
            # Verify the file exists
            if not os.path.exists(manage_py_path):
                raise Exception(f"manage.py not found at {manage_py_path}")

            Popen(
                ["python", manage_py_path, "run_scraper", query],
                cwd=project_root,  # MUST run from price_radar/ directory
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
                shell=True
            )

            return HttpResponse("Product not found - scraping started")

            # time.sleep(40)
            
            # products = list(products_collection.find({
            #     "name": {"$regex": f".*{query}.*", "$options": "i"}
            # }).limit(20))

            # if products:
                
            #     if "scraping_query" in request.session:
            #         del request.session["scraping_query"]
            #     if "scraping_started" in request.session:
            #         del request.session["scraping_started"]
            #     return render(request, "results.html", {"products": products})
            # else:
                
            #     return render(request, "results.html", {
            #         "show_error_popup": True,
            #         "error_message": f"No products found for '{query}'"
            #     })
                
        except Exception as e:
            print(f"Failed to start scraper: {e}")
            
            if "scraping_query" in request.session:
                del request.session["scraping_query"]
            if "scraping_started" in request.session:
                del request.session["scraping_started"]
                
            return render(request, "error.html", {
                "error": "Failed to start search",
                "message": str(e)
            })
        
def search_products(request, query):
    query_words = request.GET.get("query", "").strip()
    
    if not query_words:
        return []
    
    # Create regex conditions for each word
    regex_conditions = [{"name": {"$regex": f".*{re.escape(word)}.*", "$options": "i"}} 
                       for word in query_words]
    
    products = list(products_collection.find({
        "$and": regex_conditions
    }).limit(20))
    
    return products
    

    # return redirect("loading_view")


@csrf_exempt
def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse("Missing URL parameter", status=400)
    
    try:
        # Parse the image URL to determine the source
        parsed_url = urlparse(image_url)
        domain = parsed_url.netloc.lower()
        
        # Set appropriate referer based on the image source
        if 'priceoye' in domain:
            referer = 'https://priceoye.pk/'
        elif 'shophive' in domain:
            referer = 'https://shophive.com/'
        elif 'daraz' in domain:
            referer = 'https://www.daraz.pk/'
        else:
            # Generic referer for other sources
            referer = parsed_url.scheme + '://' + parsed_url.netloc + '/'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/avif,image/svg+xml,image/,/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': referer,
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'DNT': '1',
        }
        
        response = requests.get(
            image_url, 
            stream=True, 
            headers=headers, 
            timeout=10,
            allow_redirects=True,
            verify=True
        )
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', 'image/webp')
            django_response = HttpResponse(response.content, content_type=content_type)
            
            # Add comprehensive CORS headers
            django_response["Access-Control-Allow-Origin"] = "*"
            django_response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            django_response["Access-Control-Allow-Headers"] = "Content-Type"
            django_response["Cache-Control"] = "public, max-age=3600"  # Cache for 1 hour
            django_response["Vary"] = "Origin"
            
            return django_response
        else:
            print(f"Failed to fetch image from {domain}: {response.status_code}")
            return HttpResponse(f"Failed to fetch image: {response.status_code}", status=response.status_code)
            
    except requests.exceptions.Timeout:
        print(f"Timeout fetching image: {image_url}")
        return HttpResponse("Request timeout", status=504)
    except requests.exceptions.SSLError as e:
        print(f"SSL error fetching image: {e}")
        return HttpResponse("SSL error", status=502)
    except requests.exceptions.RequestException as e:
        print(f"Proxy error: {e}")
        return HttpResponse(f"Error: {str(e)}", status=500)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return HttpResponse("Internal server error", status=500)
    
def call_proxy_image(image_url):
    """Call proxy_image function and return the proxied URL"""
    if not image_url:
        return None
    
    # Return the proxy URL that React can use
    return f"http://localhost:8000/proxy_image/?url={image_url}"
    


def getProductsBySearch(request):
    query = request.GET.get("query", "").strip()
    page = int(request.GET.get("page", 1))  # Default to page 1
    per_page = 20  # Number of products per page
    sort_order = 1

    skip = (page - 1) * per_page

    # MongoDB query with pagination
    products_cursor = products_collection.find({
        "name": {"$regex": f".*{query}.*", "$options": "i"}
    }).sort("price", sort_order).skip(skip).limit(per_page)

    products = list(products_cursor)

    if products:
        data = [
            {
                'title': prod.get("name"),
                'original_price': prod.get("original_price"),
                'current_price': prod.get("current_price"),
                'previous_price': prod.get("previous_price"),
                'category': prod.get("category"),
                'url': prod.get("url"),
                'image_url': prod.get("image_url"),
                'platform': prod.get("platform")
            }
            for prod in products
        ]

        # Get total count (for frontend to know how many pages exist)
        total_count = products_collection.count_documents({
            "name": {"$regex": f".*{query}.*", "$options": "i"}
        })

        response = {
            'products': data,
            'total_count': total_count,
            'current_page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }

        return JsonResponse(response, safe=False)

    else:
        return HttpResponse("Product not present")
    

def getProductsByCategory(request):
    query = request.GET.get("query", "").strip()
    page = int(request.GET.get("page", 1))  # Default to page 1
    per_page = 20  # Number of products per page
    sort_order = 1

    skip = (page - 1) * per_page

    # MongoDB query with pagination
    products_cursor = products_collection.find({
        "category": {"$regex": f".*{query}.*", "$options": "i"}
    }).sort("price", sort_order).skip(skip).limit(per_page)

    products = list(products_cursor)

    if products:
        data = [
            {
                'title': prod.get("name"),
                'original_price': prod.get("original_price"),
                'current_price': prod.get("current_price"),
                'previous_price': prod.get("previous_price"),
                'category': prod.get("category"),
                'url': prod.get("url"),
                'image_url': prod.get("image_url"),
                'platform': prod.get("platform")
            }
            for prod in products
        ]

        # Get total count (for frontend to know how many pages exist)
        total_count = products_collection.count_documents({
            "category": {"$regex": f".*{query}.*", "$options": "i"}
        })

        response = {
            'products': data,
            'total_count': total_count,
            'current_page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }

        return JsonResponse(response, safe=False)

    else:
        return HttpResponse("Product not present")
    

def getProductsBySubCategory(request):
    query = request.GET.get("query", "").strip()
    page = int(request.GET.get("page", 1))  # Default to page 1
    per_page = 20  # Number of products per page
    sort_order = 1

    skip = (page - 1) * per_page

    # MongoDB query with pagination
    products_cursor = products_collection.find({
        "sub_category": {"$regex": f".*{query}.*", "$options": "i"}
    }).sort("price", sort_order).skip(skip).limit(per_page)

    products = list(products_cursor)

    if products:
        data = [
            {
                'title': prod.get("name"),
                'original_price': prod.get("original_price"),
                'current_price': prod.get("current_price"),
                'previous_price': prod.get("previous_price"),
                'category': prod.get("category"),
                'url': prod.get("url"),
                'image_url': prod.get("image_url"),
                'platform': prod.get("platform")
            }
            for prod in products
        ]

        # Get total count (for frontend to know how many pages exist)
        total_count = products_collection.count_documents({
            "sub_category": {"$regex": f".*{query}.*", "$options": "i"}
        })

        response = {
            'products': data,
            'total_count': total_count,
            'current_page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }

        return JsonResponse(response, safe=False)

    else:
        return HttpResponse("Product not present")
    

def getProductsByPlatform(request):
    query = request.GET.get("query", "").strip()
    page = int(request.GET.get("page", 1))  # Default to page 1
    per_page = 20  # Number of products per page
    sort_order = 1

    skip = (page - 1) * per_page

    # MongoDB query with pagination
    products_cursor = products_collection.find({
        "platform": {"$regex": f".*{query}.*", "$options": "i"}
    }).sort("price", sort_order).skip(skip).limit(per_page)

    products = list(products_cursor)

    if products:
        data = [
            {
                'title': prod.get("name"),
                'original_price': prod.get("original_price"),
                'current_price': prod.get("current_price"),
                'previous_price': prod.get("previous_price"),
                'category': prod.get("category"),
                'url': prod.get("url"),
                'image_url': call_proxy_image(prod.get("image_url")),
                'platform': prod.get("platform")
            }
            for prod in products
        ]

        # Get total count (for frontend to know how many pages exist)
        total_count = products_collection.count_documents({
            "platform": {"$regex": f".*{query}.*", "$options": "i"}
        })

        response = {
            'products': data,
            'total_count': total_count,
            'current_page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }

        return JsonResponse(response, safe=False)

    else:
        return HttpResponse("Product not present")
    


def test(request):
    url = request.GET.get("query", "").strip()
    
    if not url:
        return JsonResponse({"error": "No URL provided"}, status=400)
    
    # Build the command
    command = f'python manage.py spider_by_query "{url}"'
    
    try:
        # Run the command in current directory
        process = Popen(
            command,
            shell=True  # shell=True allows running the command as is
        )
        
        return JsonResponse({
            "status": "success", 
            "message": "Scraping command executed",
            "url": url,
            "pid": process.pid
        })
        
    except Exception as e:
        return JsonResponse({"error": f"Failed to execute command: {str(e)}"}, status=500)
    

def product_updation(stale_products):
    try:

        print("Starting updating process...")
            
        for url in stale_products:
            command = f'python manage.py spider_by_query "{url}"'

            Popen(
                command,
                shell=True
            )
                    
    except Exception as e:
        print(f"Failed to start scraper: {e}")

def sort_test(request):
    query = request.GET.get("query", "").strip()
    page = int(request.GET.get("page", 1))

    sort_order = 1
    per_page = 20
    skip_count = (page - 1)*per_page

    results= products_collection.find({
        "name": {"$regex": f".*{query}.*", "$options": "i"}
    }).sort("price", sort_order).skip(skip_count).limit(per_page)

    products = list(results)

    
    data = [
        {
            'title': prod.get("name"),
            'original_price': prod.get("original_price"),
            'current_price': prod.get("current_price"),
            'previous_price': prod.get("previous_price"),
            'category': prod.get("category"),
            'url': prod.get("url"),
            'image_url': prod.get("image_url"),
            'platform': prod.get("platform")
        }
        for prod in products
    ]

    return JsonResponse({'products': data}, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def signUp(request):

    try:
        data = json.loads(request.body)

        Username = data.get('username', '').strip()
        Email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        password2 = data.get('password2', ''). strip()

        if not (Username and Email and password and password2):
            return JsonResponse({'error': 'Please Fill out all the the fields.'}, status = 400)
        
        if password != password2:
            return JsonResponse({'error': 'Password is not matching with confirm password.'}, status= 400)
        
        if len(password) < 8:
            return JsonResponse({'error': 'Password length must not be shorter than 8 characters.'}, status= 400)
        
        try:
            validate_email(Email)
        except ValidationError:
            return JsonResponse({'error': 'Invalid email format'}, status=400)
        

        if User.objects.filter(username = Username):
            return JsonResponse({'error': 'User already exists.'}, status= 400)
        
        if User.objects.filter(email = Email):
            return JsonResponse({'error': 'User with this email already exists.'}, status= 400)
        
        user = User.objects.create_user(
            username = Username,
            password = password,
            email = Email
        )

        login(request, user)

        return JsonResponse({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def login(request):

    try:

        data = json.loads(request.body)

        Username = data.get('username', '').strip()
        Email = data.get('email', '').strip()
        password = data.get('password', '')


        if not (Username and Email):
            return JsonResponse({'error': 'Please provide Username or Email for login.'}, status = 400)

        if not password:
            return JsonResponse({'error': 'Please enter password.'}, status = 400)


        user = authenticate(request, username = Username, password = password)


        if user is not None:
            login(request, user)
            return JsonResponse({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=200)
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def logout_view(request):
    
    try:
        logout(request)
        return JsonResponse({'message': 'Logout successful'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_account_view(request):

    try:
        user = request.user
        user.delete()
        return JsonResponse({'message': 'Account deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# from django.apps import AppConfig
# from apscheduler.schedulers.background import BackgroundScheduler
# from django.http import HttpResponse

# def scheduling():
#     print("print ho rha !")

# def startSchedular(request):
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(scheduling, 'interval', seconds=10)  # every 24 hours
#     scheduler.start()
#     return HttpResponse("Scheduler started successfully!")

        

    # if request.method == 'GET':
    #     all_products = Product.objects.all()
    #     data = [{'title': prod.name, 'price': prod.original_price, 'url': prod.url, 'image_url': prod.image_url} for prod in all_products]
    #     return JsonResponse(data, safe=False)

# def search_product_view(request):
#     print("🔎 Search product function started")

#     query = request.GET.get("query", "").strip()
#     if not query:
#         return render(request, "home.html", {"error": "Please enter a valid query."})

#     if "query" in request.session:
#         del request.session["query"]  

#     products = list(products_collection.find({
#         "name": {"$regex": f".*{query}.*", "$options": "i"}
#     }))

#     if products:
#         return render(request, "results.html", {"products": products})

#     Popen(
#         ["python", "manage.py", "runscrapers", query],
#         stdout=DEVNULL, 
#         stderr=DEVNULL,
#         start_new_session=True
#     )  # Start scraping
#     request.session["query"] = query  # Save query in session
#     request.session["scraping_started"] = datetime.now().isoformat()


#     try:
#         subprocess.Popen(
#             ["python", "manage.py", "runscrapers", query],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             start_new_session=True
#         )
#     except Exception as e:
#         print(f"Failed to start scraper: {e}")
#         return render(request, "error.html", {"error": "Failed to start search"})

#     return redirect("loading_view")




# def loading_view(request):
#     # Check if we have the required session data
#     if "scraping_query" not in request.session or "scraping_started" not in request.session:
#         return redirect("home")
    
#     query = request.session["scraping_query"]
    
#     # Check if products are now available
#     products = list(products_collection.find({
#         "name": {"$regex": f".*{query}.*", "$options": "i"}
#     }).limit(20))
    
#     if products:
#         # Clear session and show results
#         del request.session["scraping_query"]
#         del request.session["scraping_started"]
#         request.session.modified = True
#         return render(request, "results.html", {"products": products})
    
#     # Check if scraping is taking too long (timeout after 2 minutes)
#     try:
#         started = datetime.fromisoformat(request.session["scraping_started"])
#         if (datetime.now() - started).total_seconds() > 120:
#             del request.session["scraping_query"]
#             del request.session["scraping_started"]
#             request.session.modified = True
#             return render(request, "error.html", {
#                 "error": "Search timed out",
#                 "query": query
#             })
#     except (ValueError, KeyError) as e:
#         print(f"Error checking timeout: {e}")
#         return redirect("home")
    
#     # If still waiting, show loading page
#     return render(request, "loading.html", {
#         "query": query
#     })




# @csrf_exempt
# def get_scraped_data_view(request):
#     try:
#         query = request.session.get("query", "").strip()
#         if not query:
#             return JsonResponse({"status": "error"}, status=400)
        
#         db = Db
        
#         # Check scraper completion
#         status = db.scraper_status.find_one({"query": query})
#         if not status or status.get("status") != "completed":
#             return JsonResponse({"status": "processing"})
            
#         # Get final results
#         products = list(db.products.find(
#             {"name": {"$regex": f".*{query}.*", "$options": "i"}},
#             {"_id": 0}
#         ))
        
#         return JsonResponse({
#             "status": "completed",
#             "results": json.loads(json_util.dumps(products))
#         })
        
#     except Exception as e:
#         return JsonResponse({"status": "error"}, status=500)
    

# from django.views.decorators.http import require_GET

# @require_GET
# def check_scraping_status(request):
#     query = request.GET.get("query")
#     if not query:
#         return JsonResponse({"status": "error", "message": "No query provided"}, status=400)
    
#     # Check cache/database first
#     cache_key = f"scraping_{query}"
#     status = cache.get(cache_key)
    
#     # If we have a status in cache and it's not failed, return it
#     if status and status.get("status") not in ["failed", "error"]:
#         return JsonResponse(status)
    
#     # Check if we have products for this query
#     products = list(products_collection.find(
#         {"name": {"$regex": f".*{re.escape(query)}.*", "$options": "i"}}
#     ).limit(1))
    
#     # If products exist, return completed status
#     if products:
#         complete_status = {"status": "completed", "product_count": len(products)}
#         cache.set(cache_key, complete_status, timeout=3600)
#         return JsonResponse(complete_status)
    
#     # If no status in cache or status was failed, start a new scraper
#     if not status or status.get("status") in ["failed", "error"]:
#         try:
#             # Start the scraper process
#             Popen(
#                 ["python", "manage.py", "run_scraper", query],
#                 cwd=settings.BASE_DIR,
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL,
#                 start_new_session=True
#             )
            
#             # Set the initial status
#             new_status = {"status": "running", "query": query, "start_time": time.time()}
#             cache.set(cache_key, new_status, timeout=3600)
#             return JsonResponse(new_status)
            
#         except Exception as e:
#             error_status = {"status": "failed", "error": str(e)}
#             cache.set(cache_key, error_status, timeout=3600)
#             return JsonResponse({"status": "error", "message": f"Failed to start scraper: {str(e)}"})
    
#     # If we reach here, just return the current status (which should be rare)
#     return JsonResponse(status or {"status": "unknown"})
    
# from django.core.cache import cache

# def start_product_search(request):
#     """Initiate product search with optimized workflow"""
#     query = request.GET.get('query', '').strip()
#     if not query:
#         return redirect('home')
    
#     # Check cache first
#     cache_key = f"scraping_{query}"
#     if cache.get(cache_key, {}).get("status") == "completed":
#         return redirect("results_view", query=query)
    
#     # Check database for existing results
#     try:
#         client = Client
#         db = Db
#         products = list(db.products.find(
#             {"name": {"$regex": f".*{re.escape(query)}.*", "$options": "i"}}
#         ).limit(20))
        
#         if products:
#             return render(request, "results.html", {"products": products})
            
#     except Exception as e:
#         print(f"Database error: {e}")
#         return render(request, "error.html", {"error": "Database error"})

#     # Initialize scraping process
#     cache.set(cache_key, {
#         "status": "starting",
#         "query": query,
#         "start_time": time.time(),
#         "last_update": time.time()
#     }, timeout=3600)  # 1 hour timeout

#     try:
#         # Start background scraping process
#         from subprocess import Popen
#         Popen([
#             "python", "manage.py", "run_scrapers",
#             query,
#             "--cache-key", cache_key
#         ], cwd=settings.BASE_DIR)
        
#         return render(request, "loading.html", {"query": query})
        
#     except Exception as e:
#         cache.set(cache_key, {
#             "status": "failed",
#             "error": str(e),
#             "failed_at": time.time()
#         }, timeout=3600)
#         return render(request, "error.html", {"error": "Failed to start search"})


# def start_product_search(request):
#     query = request.GET.get('query')
#     if not query:
#         return redirect('home')
    
#     # Store query in session
#     request.session['scraping_query'] = query
#     request.session['scraping_started_at'] = time.time()
#     request.session['scraping_status'] = 'running'
    
#     # Run the scraping command in the background
#     from subprocess import Popen
#     from django.conf import settings
#     import os
    
#     cmd = [
#         'python', 'manage.py', 'run_scrapers', 
#         query, 
#         '--session-key', request.session.session_key
#     ]
    
#     # Run the command in the background
#     Popen(cmd, cwd=settings.BASE_DIR)
    
#     # Redirect to waiting page
#     return render(request, 'waiting.html')






# @csrf_exempt
# def get_scraped_data_view(request):
#     print("🔍 Fetching scraped data...")

    
#     # Fetch the query from the session
#     query = request.session.get("query", "")
#     if not query:
#         print("❌ No query found in session.")
#         return JsonResponse([])

#     print(f"✅ Query received: {query}")

#     # Fetch data from MongoDB
#     products = list(products_collection.find({
#         "name": {"$regex": f".*{query}.*", "$options": "i"}
#     }))

#     if products:
#         print(f"✅ {len(products)} products found in DB for query: {query}")
#         return JsonResponse(products, safe=False)  # Return products as JSON

#     print("❌ No products found in MongoDB.")
#     return JsonResponse([], safe=False)


