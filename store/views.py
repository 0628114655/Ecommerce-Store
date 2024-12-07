from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.db.models import Count
import json
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Avg
from .utils import *
from django.views import View
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid

def index(request):
    form_email = Form_Email(request)
    product_reviews = get_recent_products()
    items, products_with_ratings = get_items_with_ratings(request)
    special_offers = Item.objects.filter( discount__gte = 0 ).order_by('-discount')[:2]
    categories = Category.objects.all()
    get_total = 0
    cart = 0
    try:
        cart, created = Cart.objects.get_or_create(user=request.user, complete = False)
        get_total = Favorite.objects.filter(user = request.user).count()
    except:
        device = request.COOKIES.get('device')
        if device:
            user = User.objects.get_or_create(username=device)[0]
            cart, created = Cart.objects.get_or_create(user=user, complete = False)
            get_total = Favorite.objects.filter(user=user).count()

    context = {
        'get_total' : get_total,
        "cart" : cart,
        'email' : form_email,
        "special_offers" : special_offers ,
        'recent_products' : product_reviews,
        'products' : items ,
        'items' : products_with_ratings,
        'categories' : categories,  
    }
    return render(request, 'index.html', context)

def add_to_cart(request, id):
    product = get_object_or_404(Item, id= id)
    try:
        cart, created = Cart.objects.get_or_create(user=request.user, complete = False)
    except:
        device = request.COOKIES.get('device')
        if device:
            user = User.objects.get_or_create(username=device)[0]
            cart, created = Cart.objects.get_or_create(user=user, complete = False)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
        
def update_cart_item (request):
    if request.method == 'POST':
        print("Request received!")  
        data = json.loads(request.body)
        itemId = data.get('itemID')
        action = data.get('action')
        deleteBTN = data.get('deleteBTN', None)
        print(deleteBTN, ('received'))
        item = CartItem.objects.get(product__id = itemId, cart__user = request.user, cart__complete = False)
        print('item is:', item)
        if deleteBTN == True:
            item.delete()
        if action == 'add':
            item.quantity +=1
            item.save()
        if action == 'remove':
            if item.quantity > 1:
                item.quantity -=1
                item.save()
            else:
                item.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)    

def cart(request):
    form_email = Form_Email(request)
    categories = Category.objects.all()
    try:
        cart = Cart.objects.get(user=request.user, complete =  False)
        get_total = Favorite.objects.filter(user = request.user).count()
    except:
        device = request.COOKIES.get('device')
        if device:
            user = User.objects.get_or_create(username=device)[0]
            cart, created = Cart.objects.get_or_create(user=user, complete = False)
            get_total = Favorite.objects.filter(user=user).count()
    cart_items = CartItem.objects.filter(cart=cart)
    items = Item.objects.all()
    context = {
        'items' : items,
        'get_total': get_total,
        'email' : form_email,
        'categories' : categories,
        "cart" : cart,
        'cart_items' : cart_items,  
    }
    return render (request, 'cart.html', context )

# class CheckoutView(View):
def CheckoutView(request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user, complete = False)
            get_total = Favorite.objects.filter(user = request.user).count()
        else:
            device = request.COOKIES.get('device')
            if device:
                user = User.objects.get_or_create(username=device)[0]
                cart, created = Cart.objects.get_or_create(user=user, complete = False)
                get_total = Favorite.objects.filter(user=user).count()
        form_shipping = ShippingForm()
        form_email = Form_Email(request)
        categories = Category.objects.all()
        cart_items = CartItem.objects.filter(cart=cart)
        context = {
            'form_shipping': form_shipping,
            'get_total': get_total,
            "cart" : cart,
            'email' : form_email,
            'categories' : categories,  
            'cart_items' : cart_items,  
        }

        return render(request, 'checkout.html', context) 

@login_required   
def payment_success(request):
    try:
        transactionId = datetime.now().timestamp()
        data = json.loads(request.body)
        user_info = data['userInfo']
        shipping_info = data['shippingInfo']
        if request.user.is_authenticated:
            user = request.user
            cart, created = Cart.objects.get_or_create(user=user, complete = False)
        if cart.shipping == True:
            ShippingInfo.objects.create(
                user = user,
                cart = cart,
                name = user_info['name'],
                email = user_info['email'],
                mobile = shipping_info['mobile'],
                address = shipping_info['address'],
                country = shipping_info['country'],
                city = shipping_info['city'],
                state = shipping_info['state'],
                zip_code = shipping_info['zipcode']
            )
        total = float(user_info["final_total"])
        if total == round(cart.Final_total, 2):
            cart.transaction_id = transactionId
            cart.complete = True
            cart.ordered_date = datetime.now()
        cart.save()
        print('it is done')
        
        return JsonResponse('Payment complete', safe=False)
    except Exception as e:
        return JsonResponse({'Error': str(e)}) 

@login_required   
def payment_failed(request):
    return render(request, 'payment_failed.html')

def search(request):
    form_email = Form_Email(request)
    category_count, price_count, items_count, items_category_count, product, products_with_ratings = searching(request)
    categories = Category.objects.all()
    try:
        cart = Cart.objects.get(user=request.user, complete =  False)
        get_total = Favorite.objects.filter(user = request.user).count()
    except:
        device = request.COOKIES.get('device')
        if device:
            user = User.objects.get_or_create(username=device)[0]
            cart, created = Cart.objects.get_or_create(user=user)
            get_total = Favorite.objects.filter(user=user).count()
    context = {
        'get_total' : get_total,
        "cart" : cart,
        'email' : form_email,
        'items_category_count' : items_category_count,
        'items_count':items_count,
        **category_count,
        **price_count,
        'products' : product ,
        'items' : products_with_ratings,
        'categories' : categories,  
    }
    return render(request, 'search.html', context)

def detail(request, id):
    categorie = Category.objects.values_list('name', flat=True)
    categories = Category.objects.all()
    images = Image.objects.filter(item = id)
    form_email = Form_Email(request)
    item =  get_object_or_404(Item, id = id)
    itemRatingCount = item.reviews.aggregate(Avg('rating'))['rating__avg']
    products = Item.objects.filter(category = item.category).annotate(itemRat = Avg('reviews__rating'),review_count = Count('reviews')).exclude(id = id)
    reviews = item.reviews.all()
    reviewsCount = reviews.count()
    itemRatingCount = itemRatingCount if itemRatingCount is not None else 0
    full_stars = int(itemRatingCount)
    half_star = itemRatingCount - full_stars > 0
    next_star = full_stars + 1
    products_with_ratings = []
    for product in products:
        itemRat = product.itemRat
        product_rating = itemRat if itemRat is not None else 0
        full = int(product_rating)
        half =  product_rating - full > 0
        next = full + 1
        products_with_ratings.append({
            'item' : product,
            'full' : full,
            'half' : half,
            'next' : next,
        })
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = item
            review.save()
            return redirect('detail', id = item.id )  
        else:
            print('ERROR: ', form.errors)
    else:
        form = ReviewForm()
    try:
        cart = Cart.objects.get(user=request.user, complete =  False)
        get_total = Favorite.objects.filter(user = request.user).count()
    except:
        device = request.COOKIES.get('device')
        if device:
            user = User.objects.get_or_create(username=device)[0]
            cart, created = Cart.objects.get_or_create(user=user)
            get_total = Favorite.objects.filter(user=user).count()

    context = {
        "cart" : cart,
        'email' : form_email,
        'next_star' : next_star,
        'full_stars': full_stars,
        'half_star': half_star,
        'itemRatingCount' : itemRatingCount,
        'reviewsCount': reviewsCount,
        'form' : form,
        'reviews': reviews,
        'items' : item,
        'products': products_with_ratings,
        'categorie' :categorie ,
        'images' : images,
        'categories' : categories,
        'get_total' : get_total, 
    }
    return render(request, 'detail.html', context)

def category(request, id):
    category_item= Category.objects.get(id = id)
    items = category_item.categoryItems.all()
    items = items.annotate(
            itemRat=Avg('reviews__rating'),
            review_count=Count('reviews'))
    products_with_ratings = []
    for item in items:
        itemRat = item.itemRat
        product_rating = itemRat if itemRat is not None else 0
        full = int(product_rating)
        half = product_rating - full > 0
        next = full + 1
        products_with_ratings.append({
            'items': item,
            'full': full,
            'half': half,
            'next': next,
        })
    categories = Category.objects.all()
    form_email = Form_Email(request)
    sort_by = request.GET.get('sort','title')
    paginator = request.GET.get('paginator', 10)
    get_page = request.GET.get('page', 1)
    items = items.order_by(sort_by)
    paginator_value = int(paginator)
    paginator = Paginator(items, paginator_value)
    items = paginator.get_page(get_page)
    try:
        cart = Cart.objects.get(user=request.user, complete =  False)
        get_total = Favorite.objects.filter(user = request.user).count()
    except:
        device = request.COOKIES.get('device')
        if device:
            user = User.objects.get_or_create(username=device)[0]
            cart, created = Cart.objects.get_or_create(user=user)
            get_total = Favorite.objects.filter(user=user).count()

    context = {
        'product' : items,
        'get_total' : get_total,
        "cart" : cart,
        'categories' : categories,  
        'email': form_email,
        'category' : category_item,
        'items' : products_with_ratings,
    }
    return render(request, 'category.html', context)

def add_favorites(request, id):
    referer = request.META.get('HTTP_REFERER', '/')
    if referer.endswith('/favorites/'):
        try:
            item = Favorite.objects.get(product__id = id, user=request.user)
        except:
            device = request.COOKIES.get('device')
            if device:
                user = User.objects.get_or_create(username=device)[0]
                item = Favorite.objects.get(product__id = id, user=user)
        item.delete()
    else:
        try:
            item = Item.objects.get(id = id)
            item, created = Favorite.objects.get_or_create(user = request.user, product = item) 
        except:
            item = Item.objects.get(id = id)
            device = request.COOKIES.get('device')
            if device:
                user = User.objects.get_or_create(username=device)[0]
                item, created = Favorite.objects.get_or_create(user= user, product = item) 
    return redirect(request.META.get('HTTP_REFERER', '/'))

def favorites(request):
    try:           
        form_email = Form_Email(request)
        categorie = Category.objects.values_list('name', flat=True)
        categories = Category.objects.all()
        try:
            cart, created = Cart.objects.get_or_create(user=request.user, complete =  False)
            get_total = Favorite.objects.filter(user = request.user).count()
            items = Favorite.objects.filter(user = request.user).annotate(
                itemRat=Avg('product__reviews__rating'),
                review_count=Count('product__reviews'))
        except:
            device = request.COOKIES.get('device')
            if device:
                user = User.objects.get_or_create(username=device)[0]
                cart, created = Cart.objects.get_or_create(user=user)
                get_total = Favorite.objects.filter(user=user).count()
                items = Favorite.objects.filter(user = user).annotate(
                itemRat=Avg('product__reviews__rating'),
                review_count=Count('product__reviews'))
        products_with_ratings = []
        for item in items:
            itemRat = item.itemRat
            product_rating = itemRat if itemRat is not None else 0
            full = int(product_rating)
            half = product_rating - full > 0
            next = full + 1
            products_with_ratings.append({
                'favorites': item,
                'full': full,
                'half': half,
                'next': next,
            })
    except:
        cart = None
        get_total = 0
        items = None
        products_with_ratings = None
    context = {
        'get_total' : get_total,
        'items' : products_with_ratings,
        "cart" : cart,
        'email': form_email,
        'categorie' : categorie,
        'categories' : categories,  
    }
    return render(request, 'favorites.html', context)

def contact(request):
    form_email = Form_Email(request)
    categories = Category.objects.all()
    form = ContactUs(request.POST or None)
    try:
        cart, created = Cart.objects.get_or_create(user=request.user, complete =  False)
        get_total = Favorite.objects.filter(user = request.user).count()
    except:
        device = request.COOKIES.get('device')
        if device:
            user = User.objects.get_or_create(username=device)[0]
            cart, created = Cart.objects.get_or_create(user=user)
            get_total = Favorite.objects.filter(user=user).count()
    if form.is_valid():
        form.save()
    context = {
        'get_total': get_total,
        "cart" : cart,
        'email' :form_email,
        'form' : form,
        'categories' : categories,  

    }
    return render(request, 'contact.html', context)

def login_view(request):
    categories = Category.objects.all() 
    categorie = Category.objects.values_list('name', flat=True)
    items = Item.objects.all()
    form_email = Form_Email(request)
    try:
        cart, created = Cart.objects.get_or_create(user=request.user, complete = False)
        get_total = Favorite.objects.filter(user = request.user).count()
    except:
        device = request.COOKIES.get('device')
        if device:
            user = User.objects.get_or_create(username=device)[0]
            cart, created = Cart.objects.get_or_create(user=user)
            get_total = Favorite.objects.filter(user=user).count()
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username = username, password = password)
        login(request, user)
        device = request.COOKIES.get('device')
        if device:
                anonymous_cart = Cart.objects.filter(user__username=device, complete=False).first()
                print('cart is:', anonymous_cart)
                if anonymous_cart:
                    user_cart, created = Cart.objects.get_or_create(user=user, complete=False)
                    anonymous_cart_items = CartItem.objects.filter(cart=anonymous_cart)
                    for item in anonymous_cart_items:
                        existing_item = CartItem.objects.filter(cart = user_cart, product = item.product).first()
                        if existing_item:
                            existing_item.quantity += item.quantity
                            existing_item.save()
                        else:
                            item.cart = user_cart
                        item.save()
                    anonymous_cart.delete()

                anonymous_favorites = Favorite.objects.filter(user__username=device)
                if anonymous_favorites.exists():
                    for item in anonymous_favorites:
                        fav_item, created = Favorite.objects.get_or_create(
                            user=user,
                            product=item.product
                        )
                    anonymous_favorites.delete()
                    
        if next:
            return redirect(next)
        return redirect('/')
    context = {
        'get_total': get_total,
        "cart" : cart,
        'email':form_email,
        'form' : form,
        'items' : items,
        'categorie' : categorie,
        'categories' : categories,  
    }
    return render(request, 'login.html', context)

def signup(request):
    try:
        cart, created = Cart.objects.get_or_create(user=request.user, complete = False)
        get_total = Favorite.objects.filter(user = request.user).count()
    except:
        device = request.COOKIES.get('device')
        if device:
            user = User.objects.get_or_create(username=device)[0]
            cart, created = Cart.objects.get_or_create(user=user)
            get_total = Favorite.objects.filter(user=user).count()
    categories = Category.objects.all()
    categorie = Category.objects.values_list('name', flat=True)
    items = Item.objects.all()
    form_email = Form_Email(request)
    next = request.GET.get('next')
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit = False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username = user.username, password = password)
        login(request, new_user)
        if next:
            return redirect(next)
        return redirect('/')
    context = {
        'get_total' : get_total,
        "cart" : cart,
        'categories' : categories,  
        'email': form_email,
        'form' : form,
        'items' : items,
        'categorie' : categorie,
    }
    return render(request, 'signup.html', context)

def signout(request):
    logout(request)
    
    return redirect('/login/')

