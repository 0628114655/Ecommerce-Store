from django.urls import path, include
from . import views
from .views import CheckoutView 
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name = 'index'), 
    path('cart/', views.cart, name = 'cart'), 
    path('add_to_cart/<int:id>/', views.add_to_cart, name = 'add_to_cart'), 
    path('update_cart_item/', views.update_cart_item, name = 'update_cart_item'), 
    path('checkout/', CheckoutView, name = 'checkout'), 
    path('add_favorites/<int:id>/', views.add_favorites, name = 'add_favorites'), 
    path('favorites/', views.favorites, name = 'favorites'), 
    path('contact/', views.contact, name = 'contact'), 
    path('detail/<int:id>/', views.detail, name = 'detail'), 
    path('category/<int:id>/', views.category, name = 'category'), 
    path('search/', views.search, name = 'search'), 
    path('login/', views.login_view, name = 'login'),
    path('signup/', views.signup, name = 'signup'),
    path('logout/', views.signout, name = 'logout'),
    path('paypal', include('paypal.standard.ipn.urls')),
    path('payment_success/', views.payment_success, name = 'payment_success'),
    path('payment_failed/', views.payment_failed, name = 'payment_failed'),


]+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)