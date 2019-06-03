from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, resolve
from django.contrib.auth import authenticate, login, logout, models

# Create your views here.
def LoginForm(request) :
    return render(request,"login/Login.html")

def SignUpForm(request) :
    return render(request,"login/SignUp.html")

def LoginSubmit(request) :
    username = request.POST['uname']
    password = request.POST['psw']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('home'))
    else :
        return HttpResponseRedirect(reverse('loginform'))

def Logout(request) :
    logout(request)
    return HttpResponseRedirect(reverse('loginform'))

def createUser(request) :
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
    newUser = models.User.objects.create_user(username, email, password)
    return HttpResponseRedirect('../signupsuccess')

def SignUpSuccess(request):
    return render(request,'login/user_created.html',{})
