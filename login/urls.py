from django.contrib import admin
from django.urls import path, include
from .views import LoginForm, LoginSubmit, Logout, SignUpForm, createUser, SignUpSuccess
from imgapp import urls

urlpatterns = [
    path('',LoginForm,name ='loginform'),
    path('loginsubmit/',LoginSubmit,name='loginsubmit'),
    path('logout/',Logout,name='logout'),
    path('signup/',SignUpForm,name='signup'),
    path('createuser/',createUser,name='createuser'),
    path('signupsuccess/',SignUpSuccess,name='signupsuccess'),
]