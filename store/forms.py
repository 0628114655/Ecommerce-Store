from typing import Any
from django import forms
from django.contrib.auth import authenticate, get_user_model
from .models import *

User = get_user_model()
class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-custom-class', 'placeholder' : 'Enter Your Username ' }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control my-custom-class', 'placeholder' : 'Enter Your Password'}))

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username = username, password = password)
            if not user:
                raise forms.ValidationError('User does not exist.')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect password')
            if not user.is_active:
                raise forms.ValidationError('User is not active')
            return super(UserLoginForm, self).clean(*args, **kwargs)
        
class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label='Email Address',widget=forms.EmailInput( attrs={'class':'form-control my-custom-class', 'placeholder' : 'Enter Your Email ' }))
    email2 = forms.EmailField(label='Confirm Email', widget=forms.EmailInput( attrs={'class':'form-control my-custom-class', 'placeholder' : 'Confirm Your Email ' }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control my-custom-class', 'placeholder' : 'Enter Your Password'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-custom-class', 'placeholder' : 'Enter Your Username ' }))
    class Meta:
        model = User
        fields = [
            'username', 'email', 'email2', 'password'
        ]
    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        username_error = User.objects.filter(username = username)
        if username_error.exists():
            raise forms.ValidationError('This username already exists')
        if email != email2:
            raise forms.ValidationError("Emails doesn't match")
        email_qs = User.objects.filter(email = email)
        if email_qs.exists():
            raise forms.ValidationError ("this email is already being used")
        return super(UserRegistrationForm, self).clean(*args, **kwargs)
    
class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating' : forms.RadioSelect(choices = [(i, f'⭐{i}') for i in range(1, 6)]),

        }

class ContactUs(forms.ModelForm):
    name = forms.CharField(widget = forms.TextInput(attrs= {'class' : 'form-control', 'placeholder': 'Enter your name'}))
    email = forms.EmailField(widget = forms.EmailInput(attrs= {'class' : 'form-control', 'placeholder': 'Enter your email'}))
    subject = forms.CharField(widget = forms.TextInput(attrs= {'class' : 'form-control', 'placeholder': 'Enter your subject'}))
    message = forms.CharField(widget = forms.TextInput(attrs= {'class' : 'form-control', 'placeholder': 'Enter your message'}))
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message'] 

class GetEmail(forms.ModelForm):
    email = forms.EmailField(widget = forms.EmailInput(attrs= {'class' : 'form-control', 'placeholder': 'Your Email Address'}))
    label = ''
    class Meta:
        model = Email
        fields = [ 'email'] 
      
class ShippingForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-custom-class', 'placeholder' : 'Your Name', 'id': 'name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control my-custom-class', 'placeholder' : 'example@email.com', 'id': 'email'}))
    mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-custom-class', 'placeholder' : '+123 456 789', 'id': 'mobile'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-custom-class', 'placeholder' : 'Your First Address', 'id': 'address'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-custom-class', 'placeholder' : 'Your City', 'id': 'city'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-custom-class', 'placeholder' : 'Your State', 'id': 'state'}))
    zip_code = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control my-custom-class', 'placeholder' : '123', 'id': 'zipcode'}))
    country = forms.Select(attrs={'class': 'form-control my-custom-class', 'id': 'country'})

    class Meta:
        model = ShippingInfo
        fields = ['name','email','mobile', 'address', 'country', 'city','state','zip_code']
