import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, resolve
from django.contrib.auth import authenticate, login, logout, models
from ImageManagementSystem.settings import MONGO_CONNECTION_URL,MONGO_DATABASE
from pymongo import MongoClient

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

        # save the user login status
        client = MongoClient(MONGO_CONNECTION_URL)
        db = client[MONGO_DATABASE]
        col = db['login']
        doc = {
            'username' : user.username,
            'userID' : user.pk,
            'timestamp' : str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')),
            'status' : 'LOGGED_IN'
        }
        col.insert_one(doc)

        return HttpResponseRedirect(reverse('home'))
    else :
        return HttpResponseRedirect(reverse('loginform'))

def Logout(request) :
    # save user log out status 
    client = MongoClient(MONGO_CONNECTION_URL)
    db = client[MONGO_DATABASE]
    col = db['login']
    doc = {
        'username' : request.user.username,
        'userID' : request.user.pk,
        'timestamp' : str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')),
        'status' : 'LOGGED_OUT'
    }
    col.insert_one(doc)

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
