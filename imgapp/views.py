## @package views
#
# handle requested views 

from django.shortcuts import render, render_to_response,HttpResponse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
import datetime
import os
from .MongoQuery import MongoQuery
import shutil
import ast
from .forms import UserForm, ProfileForm, User
from galactica_imanage.settings import BASE_DIR, DATAPATH
from .uploadThreadClass import UpdateMongo_Thread, delete_User_Collection
import json

# create media directories
if not os.path.exists('uploads') :
    os.mkdir('uploads')
if not os.path.exists('imgapp/static') :
    os.mkdir('imgapp/static')

## static path
STATICPATH = BASE_DIR+'/imgapp/static'

## objectslist = class names 
with open("imgapp/categories.txt",'r') as f:
    objectslist = json.load(f)

## render upload images form template, not being used in imanage branch
# @param request view request
def Form(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin:login'))
    return render(request, "imgapp/upload.html", {})

## upload images after upload form is submitted, not being used in imanage branch
# @param request view request
def Upload(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin:login'))
    userID = request.user.pk    
    # save the image files in the data directory
    file_list = request.FILES.getlist("files")
    dataset = request.POST['dataset']
    imagetype = request.POST['imagetype']
    path_dataset = os.path.join(DATAPATH,dataset)
    path_imagetype = os.path.join(path_dataset,imagetype)
    timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    for count, x in enumerate(file_list):
        # print(type(x)) # class object of django image type
        def process(f):
            if not os.path.exists(path_dataset) :
                os.mkdir(path_dataset)
            if not os.path.exists(path_imagetype) :
                os.mkdir(path_imagetype)
            with open(path_imagetype+'/'+'('+timestamp+')'+ str(x), 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
        process(x)

    # update mongo database in a separate thread,
    # *add object detection in this thread,
    update_thread = UpdateMongo_Thread(dataset,imagetype,path_imagetype,timestamp,userID)
    update_thread.start()
    return HttpResponseRedirect(reverse('updated'))

## images uploaded confirmation, not being used in imanage branch
# @param request view request
def UpdatedMongo(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin:login'))
    return render(request, "imgapp/DatabaseUpdated.html", {})

## drop user collection, not being used in the imanage branch
# @param request view request
def delete(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin:login'))
    success = delete_User_Collection(request.user.pk)

    if (success==-1) :
        return render(request,"imgapp/Collection_dropped.html",{'msg' : "No data to delete!"})
    return render(request,"imgapp/Collection_dropped.html",{'msg' : "Deletion Successful!"})

## query images form
# @param request view request
def QueryObject(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin:login'))

    context = {'objectslist' : sorted(objectslist.items())}
    return render(request,"imgapp/QueryObject.html",context)

## format datetime (change "%Y-%M-%DT%H:%M" to "%Y-%M-%D %H:%M:%S")
# @param time timestamp returned by the query form
def format_datetime(time) :
    if (time == "") :
        return ""
    sep = time.find('T')
    date = time[:sep]
    time = time[sep+1:]
    time = time + ":00"
    formatted_datetime = date+" "+time
    return formatted_datetime

## process query, search on MongoDB and write the resulting template 
# @param request view request
def QueryObjectResult(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin:login'))
    objects = request.POST.getlist('queryvalue')

    searchtype = request.POST['searchtype']

    create_start = format_datetime(request.POST['lower_datetime'])
    create_till = format_datetime(request.POST['upper_datetime'])

    QueryMongo = MongoQuery()
    result = os.path.join(STATICPATH,'imgapp')
    if os.path.exists(result) :
        shutil.rmtree(result)
    os.mkdir(result)
    imageids = {}
    if (searchtype=="COCO") :
        imageids = QueryMongo.FindObjectsCOCO(objects)
    else :
        userID = request.user.pk
        imageids = QueryMongo.custom_search(objects,userID,searchtype,create_start,create_till)
    if (len(imageids)==0) :
        return render_to_response('imgapp/NoImagesFound.html')
    return Showresults_Objects(result)

## show results for the queries,modifies the template to show the required images 
# @param request view request
def Showresults_Objects(result) :

    base = "{% extends 'admin/base_site.html'%}"
    thumnailstyle = "<head><style>.thumbnail {text-align: right;}</style></head>"
    response = base+"{% block content %}"+thumnailstyle+"<h1>Image Results</h1><hr><div class=\"row\">{% load static %}"
    filenames = os.listdir(result)
    for file in filenames :
        path = os.path.join('imgapp',file)
        viewbutton = "<a href=\" {% static \""+path+"\" %}\" class=\"btn btn-default btn-sm\"><span class=\"icon-picture\"></span> </a>"
        downloadButton = "<a href=\" {% static \""+path+"\" %}\" download class=\"btn btn-default btn-sm\"><span class=\"icon-download\"></span> </a>"
        showimage = "<div class=\"thumbnail\" ><img src=\" {% static \""+path+"\" %}\" alt = "+file+" >"+file+"  "+downloadButton+"  "+viewbutton+"</div>"
        response = response +showimage
    response = response + "</div>{% endblock %}"
    file = open("imgapp/templates/imgapp/Showresults_Objects.html",'w')
    file.write(response)
    file.close()
    return render_to_response("imgapp/Showresults_Objects.html")

## render sign_up form and create staff user when form is submitted 
# @param request view request
def SignUp_Form(request) :

    user_form = UserForm()
    profile_form = ProfileForm()
    if (request.method == 'POST') :
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # commit = False to not save this to db yet
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            email = user_form.cleaned_data['email']

            user = User.objects.create_user(username=username, email=email,is_staff=True)
            user.set_password(password)
            user.save()
            
            profile = profile_form.save(commit=False)
            print(profile.company,"#####################")
            # make the user a staff
            user.is_staff = True
            # now saved the user to the db
            profile.user = user
            print(profile.company,"#####################")

            # user.save()
            profile.save()
            return HttpResponseRedirect(reverse('admin:login'))
        else :
            return render(request,'admin/SignUp.html',{'user_form':user_form,'profile_form':profile_form})
    
    else :
        return render(request,'admin/SignUp.html',{'user_form':user_form,'profile_form':profile_form})


## render description template
# @param request view request  
def description(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admin:login'))
    return render(request,'imgapp/description.html',{})