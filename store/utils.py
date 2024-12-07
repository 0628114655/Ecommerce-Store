# utils.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Category
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from .forms import *
import requests
from requests.auth import HTTPBasicAuth
import base64

def get_items_with_ratings(request):
    items = Item.objects.annotate(
        itemRat=Avg('reviews__rating'),
        review_count=Count('reviews')).order_by('id') 
    products_with_ratings = []
    for item in items:
        itemRat = item.itemRat
        product_rating = itemRat if itemRat is not None else 0
        full = int(product_rating)
        half = product_rating - full > 0
        next = full + 1
        products_with_ratings.append({
            'product': item,
            'full': full,
            'half': half,
            'next': next,
        })
    paginator = request.GET.get('paginator', 30)
    paginator_value = int(paginator)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(items, paginator_value)
    items = paginator.get_page(page_number)
    return items, products_with_ratings

def get_recent_products():
    items = Item.objects.annotate(
    itemRat=Avg('reviews__rating'),
    review_count=Count('reviews')
    )
    recent_products = items.order_by('-created_date')[:8]
    product_reviews = []
    for item in recent_products:
        itemRat = item.itemRat
        product_rating = itemRat if itemRat is not None else 0
        full = int(product_rating)
        half = product_rating - full > 0
        next = full + 1
        product_reviews.append({
            'item': item,
            'full': full,
            'half': half,
            'next': next,
        })
    return product_reviews

def paginate_items(request, items, default_per_page=30):
    paginator_value = int(request.GET.get('paginator', default_per_page))
    page_number = request.GET.get('page', 1)
    paginator = Paginator(items, paginator_value)
    return paginator.get_page(page_number)

def searching(request):
    form = SearchForm(request.GET)
    results = []
    sort_by = request.GET.get('sort','title')
    price_range = request.GET.get('filter')
    get_category = request.GET.get('category')
    page_number = request.GET.get('page', 1)
    paginator = request.GET.get('paginator', 10)
    if form.is_valid():
        query = form.cleaned_data['query']
        results = Item.objects.filter(title__icontains = query).annotate(itemRat = Avg('reviews__rating'),review_count = Count('reviews'))
    if results:
        items = results.order_by(sort_by)
    else:
        return {}, {}, 0, 0, [], []
    if price_range:
        if price_range == 'all':
            products =  items.order_by(sort_by)
        elif price_range != 'all':
            try:
                price_min, price_max = map(int, price_range.split('-'))
                products = items.filter(price__gte=price_min, price__lte=price_max)
            except ValueError:
                return {}, {}, 0, 0, [], []

    else:
        products = items.order_by(sort_by)
    if get_category:
        if get_category == 'category-all':
            product = products
        elif  get_category != 'category-all':
            product = products.filter(category__name = get_category)
    else:
        product = products
    paginator_value = int(paginator)
    paginator = Paginator(product, paginator_value)
    product = paginator.get_page(page_number)    
    products_with_ratings = []
    for item_in_page in product:
        itemRat = item_in_page.itemRat
        product_rating = itemRat if itemRat is not None else 0
        full = int(product_rating)
        half =  product_rating - full > 0
        next = full + 1
        products_with_ratings.append({
            'product' : item_in_page,
            'full' : full,
            'half' : half,
            'next' : next,
        })
    category_count = {
        'men': items.filter(category__name = 'Men Fashion', title__in=products.values_list('title', flat=True)).count(),
        'kids': items.filter(category__name = 'Kids Fashion', title__in=products.values_list('title', flat=True)).count(),
        'clothes': items.filter(category__name = 'Clothes', title__in=products.values_list('title', flat=True)).count(),
        'shoes': items.filter(category__name = 'Shoes', title__in=products.values_list('title', flat=True)).count(),
    }
    items_category_count =sum (value  for key , value in category_count.items())
    items_count = items.count()
    price_count = {
    'price1' : items.filter(price__gte=0, price__lte=100).count(),
    'price2' : items.filter(price__gte=100, price__lte=200).count(),
    'price3' : items.filter(price__gte=200, price__lte=300).count(),
    'price4' : items.filter(price__gte=300, price__lte=400).count(),
    'price5' : items.filter(price__gte=400, price__lte=500).count()}

    return category_count, price_count, items_count, items_category_count, product, products_with_ratings
   
   
def Form_Email(request):
    form_email = GetEmail(request.POST or None)
    if form_email.is_valid():
        form_email.save()

    return form_email

def get_access_token(self):
        # هذا الكود للحصول على access token يمكن تعديله ليتناسب مع الطريقة التي تخزن بها التوكن في تطبيقك.
        client_id = 'ATiVzx0MfHLiaLNji0il0CHkAdX_nO3JAfJHI76TPvedEXPeRoCWl4jAZgnyj9QHSUdrs8OatA8K5lnA'
        client_secret = 'EJ38s-FFLqkO-ghlv03H6YVS9raLwa8NvzZxoLR0VnH7nmVZk8sk8VP_QXM6AEFbXy95aSTGqndhOLys'
        auth_str = f'{client_id}:{client_secret}'
        base64_auth_str = base64.b64encode(auth_str.encode()).decode()
        url = 'https://api-m.sandbox.paypal.com/v1/oauth2/token'
        data = {'grant_type': 'client_credentials'}
        headers = {
            'Authorization': f'Basic {base64_auth_str}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise Exception(f'Error: {response.status_code}, {response.text}')
        

def create_paypal_order(amount, access_token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }
    data = {
        'intent': 'CAPTURE',
        'purchase_units': [{
            'amount': {
                'currency_code': 'USD',
                'value': f'{amount:.2f}'
            }
        }]
    }
    response = requests.post(
        'https://api-m.sandbox.paypal.com/v2/checkout/orders',
        json=data,
        headers=headers
    )
    if response.status_code == 201:
        return {'status': 'success', 'order_id': response.json()['id']}
    else:
        return {'status': 'error', 'message': response.json()}

