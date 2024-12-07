from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import *
from django.utils import timezone
from django_countries.fields import CountryField


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length = 100, null = True)
    def __str__(self) :
        return self.name
    
class Size(models.Model):
    name = models.CharField(max_length = 100)
    def __str__(self) :
        return self.name
    
class Color(models.Model):
    name = models.CharField(max_length = 100)
    def __str__(self) :
        return self.name

class Item(models.Model):
    title = models.CharField(max_length = 100)
    subtitle = models.TextField( max_length = 300 ,null = True, blank = True)
    priceBeforDiscount = models.FloatField(default = 0)
    discount = models.FloatField(default= 0.0)
    price = models.FloatField(default = 0.0)
    image = models.ImageField(null=True)
    size = models.ManyToManyField(Size,  blank=True)
    color = models.ManyToManyField(Color,  blank=True)
    category = models.ForeignKey(Category, related_name = 'categoryItems', on_delete = models.SET_NULL, null = True)
    description = models.TextField(max_length = 500, null = True)
    created_date = models.DateTimeField(auto_now_add=True, null = True)
    information = models.TextField(null = True, blank = True )
    digital = models.BooleanField(default = False)
    shipping= models.FloatField(default = 0)
    def __str__(self):
        return self.title
    @property
    def imageURL(self):
        if self.image:
            return self.image.url
        else:
            return ''
    def save(self, *args, **kwargs):
        discount = self.discount
        self.price = self.priceBeforDiscount * (1  - discount /100)
        super(Item, self).save(*args, **kwargs)
    @property
    def is_new(self):
        return timezone.now() - self.created_date <= timedelta(days=7) 

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    products = models.ManyToManyField(Item, through='CartItem')
    complete = models.BooleanField(default = False)
    start_date = models.DateTimeField(auto_now_add = True, blank = True, null = True)
    ordered_date = models.DateTimeField(blank = True, null = True)
    transaction_id = models.CharField(max_length= 100 ,null = True)
    def __str__(self):
        if self.complete == True:
            return f'Complete Cart of {self.user.username}[{self.transaction_id}]'
        else:
            return f"Cart of {self.user.username}"
    @property
    def shipping(self):
        shipping = False
        items = self.cart_items.all()
        for i in items:
            if i.product.digital == False:
                shipping = True
        return shipping 
    @property
    def get_total_price(self):
        return sum( item.product.price * item.quantity for item in self.cart_items.all())
    @property
    def get_total_quantity(self):
        return sum( item.quantity for item in self.cart_items.all())
    @property
    def get_total_shipping(self):
        return sum (item.product.shipping for item in self.cart_items.all())
    @property
    def Final_total(self):
        return self.get_total_price + self.get_total_shipping

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name = 'cart_items')
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def get_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.title} (x{self.quantity})({self.cart})"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    product = models.ForeignKey(Item, on_delete = models.CASCADE, related_name = 'reviews')
    rating = models.IntegerField(choices = [(i, f'{i} ⭐') for i in range(1, 6)])
    comment = models.TextField(max_length = 1000)
    created_date = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f'Review by {self.user.username} for {self.product.title}'
       
class Image(models.Model):
    item = models.ForeignKey(Item, related_name= 'images', on_delete = models.CASCADE)
    image = models.ImageField(null= True)
    def __str__(self):
        return self.item.title
    @property
    def imageURL(self):
        if self.image:
            return self.image.url
        else:
            return ''
    
class Contact(models.Model):
    name = models.CharField(max_length = 50)
    email = models.EmailField()
    subject = models.CharField(max_length = 100)
    message = models.TextField()

    def __str__(self) -> str:
        return f'Message from {self.name} about {self.subject} '
    
class Email(models.Model):
    email = models.EmailField()
    def __str__(self):
        return self.email
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    product = models.ForeignKey(Item, related_name = 'favorite_product', on_delete = models.CASCADE)

class ShippingInfo(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
    name = models.CharField(max_length = 50, blank = True, null = True)    
    email = models.EmailField()  
    mobile = models.CharField(max_length = 50 ,blank = True, null = True)  
    address = models.CharField(max_length = 200, blank = True, null = True)  
    country = CountryField(blank_label = 'select country')  
    city = models.CharField(max_length = 100, blank = True, null = True)
    state = models.CharField(max_length = 100, blank = True, null = True)
    zip_code = models.CharField(max_length = 50, blank = True, null = True)
    cart = models.ForeignKey(Cart, on_delete = models.SET_NULL, null = True)
    date_added = models.DateTimeField(auto_now_add = True, null = True)
    shipped = models.BooleanField(default = False)

    def __str__(self):
        if self.shipped == True:
            return str(f'The address transaction id is: {self.cart.transaction_id}, and it is shipped')
        else:
            return str(f'The address transaction id is: {self.cart.transaction_id}')
