##@package forms
# 
# model forms 

from django.forms import ModelForm
from django import forms 
from .models import Profile
from django.contrib.auth.models import User

## UserForm 
#
# Extends ModelForm.\n 
# Uses django User model.\n 
# Form fields are username, password and email.\n
# Used in Sign Up form.   
class UserForm(ModelForm) :

    ## meta class
    class Meta:
        model = User
        fields = ('username', 'password', 'email')

## ProfileForm
#
# Extends ModelForm.\n
# Uses the Profile Model in the models.py module.\n
# Form fields are company name.\n
# Can be used to add extra fields that are not in the Django User model.\n 
# Used in Sign Up form.
class ProfileForm(ModelForm) :
    
    ## meta class
    class Meta:
        model = Profile
        fields = ('company',)

