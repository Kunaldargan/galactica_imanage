from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import datetime
import os
from .MongoQuery import MongoQuery
from .utils import Utils
import shutil
import ast
from ImageManagementSystem.settings import BASE_DIR
from .uploadThreadClass import UpdateMongo_Thread, delete_User_Collection
import json

# create media directories
if not os.path.exists('data') :
    os.mkdir('data')
if not os.path.exists('imgapp/static') :
    os.mkdir('imgapp/static')

# Instantiate the Utils Object
Utils_Object = Utils()
# Image files saved here
DATAPATH = os.path.join(BASE_DIR,'data')
# static path
STATICPATH = BASE_DIR+'/imgapp/static'

# objects list
with open(os.path.join(BASE_DIR,'App_Settings.json')) as f :
    settings = json.load(f)
with open(settings["darknet"]["names"],'r') as c:
    classes = [x.rstrip() for x in c.readlines()]

objectslist = classes


# render home screen template
def Home(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    return render(request,"imgapp/home.html", {'username':request.user.username})

# render upload images form template
def Form(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    return render(request, "imgapp/upload.html", {})

# upload images process
def Upload(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    userID = request.user.pk    
    # save the image files in the data directory
    file_list = request.FILES.getlist("files")
    dataset = request.POST['dataset']
    imagetype = request.POST['imagetype']
    path_dataset = os.path.join(DATAPATH,str(userID)+"_"+dataset)
    path_imagetype = os.path.join(path_dataset,str(userID)+"_"+imagetype)
    timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))
    
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
    update_thread = UpdateMongo_Thread(dataset,imagetype,path_imagetype,Utils_Object,timestamp,userID)
    update_thread.start()
    return HttpResponseRedirect(reverse('updated'))

# render database updated template after uploading the metadata on mongo
def UpdatedMongo(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    return render(request, "imgapp/DatabaseUpdated.html", {})


# drop user collection
def delete(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    success = delete_User_Collection(request.user.pk)

    if (success==-1) :
        return render(request,"imgapp/Collection_dropped.html",{'msg' : "No data to delete!"})
    return render(request,"imgapp/Collection_dropped.html",{'msg' : "Deletion Successful!"})


# Query key-value pairs template
def QueryMongo(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    return render(request, "imgapp/QueryDatabase.html", {})

# parse input for query key-value spaces
def RemoveSpaces(object) :
    newObj = ""
    for i in object :
        if (i!=" "):
            newObj = newObj+i
    return newObj

# find images with query key-value pairs
def QueryResults(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    QueryMongo = MongoQuery()
    queryfield = request.POST['queryfield']
    queryval = request.POST['queryvalue']
    query_field_list = queryfield.split(',')
    query_val_list = queryval.split(',')
    query_dict = {}
    for i in range(len(query_field_list)):
        query_field_list[i] = RemoveSpaces(query_field_list[i])
        query_val_list[i] = ast.literal_eval(query_val_list[i])
        query_dict.update({query_field_list[i] : query_val_list[i]})
    imagenames = QueryMongo.Find_Key_Val(query_dict,request.user.pk)
    if (len(imagenames)==0) :
        return render_to_response('imgapp/NoImagesFound.html')
    result = os.path.join(STATICPATH,'imgapp')
    if os.path.exists(result) :
        shutil.rmtree(result)
    os.mkdir(result)
    return Showresults_keyValue(imagenames,result)

# query for objects in images (template)
def QueryObject(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))

    context = {'objectslist' : objectslist}
    return render(request,"imgapp/QueryObject.html",context)

# find images with query objects
def QueryObjectResult(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    objects = request.POST.getlist('queryvalue')
    if (len(objects)==0) :
        return render_to_response('imgapp/NoImagesFound.html')
    searchtype = request.POST['searchtype']
    QueryMongo = MongoQuery()
    result = os.path.join(STATICPATH,'imgapp')
    if os.path.exists(result) :
        shutil.rmtree(result)
    os.mkdir(result)
    imageids = {}
    if (searchtype=="COCO") :
        imageids = QueryMongo.FindObjectsCOCO(objects,Utils_Object)
    else :
        userID = request.user.pk
        imageids = QueryMongo.custom_search(objects,userID,searchtype)
    if (len(imageids)==0) :
        return render_to_response('imgapp/NoImagesFound.html')
    return Showresults_Objects(result)

# show results for Object queries,modifies the template to show the images required
def Showresults_Objects(result) :
    base = "{% extends 'imgapp/base.html' %}"
    response = base+"{% block content %}<h1>Image Results</h1><hr><div class=\"row\">{% load static %}"
    filenames = os.listdir(result)
    for file in filenames :
        path = os.path.join('imgapp',file)
        viewbutton = "<a href=\" {% static \""+path+"\" %}\" class=\"btn btn-primary btn-sm\"><span class=\"glyphicon glyphicon-picture\"></span> </a>"
        downloadButton = "<a href=\" {% static \""+path+"\" %}\" download class=\"btn btn-success btn-sm\"><span class=\"glyphicon glyphicon-download-alt\"></span> </a>"
        showimage = "<div class=\"col-md-4\"><div class=\"thumbnail\" ><img src=\" {% static \""+path+"\" %}\" alt = "+file+" >"+file+"  "+downloadButton+"  "+viewbutton+"</div></div>"
        response = response +showimage
    response = response + "</div>{% endblock %}"
    file = open("imgapp/templates/imgapp/Showresults_Objects.html",'w')
    file.write(response)
    file.close()
    return render_to_response("imgapp/Showresults_Objects.html")

# show results for key value queries,modifies the template to show the images required
def Showresults_keyValue(paths,destPath) :
    base = "{% extends 'imgapp/base.html' %}"
    response = base+"{% block content %}<h1>Image Results</h1><hr><div class=\"row\">{% load static %}"
    for path in paths :
        path = shutil.copy(path,destPath)
        filename = path[path.rfind('/')+1:]
        newpath = os.path.join('imgapp',filename)
        viewbutton = "<a href=\" {% static \""+newpath+"\" %}\" class=\"btn btn-primary btn-sm\"><span class=\"glyphicon glyphicon-picture\"></span> </a>"
        downloadButton = "<a href=\" {% static \""+newpath+"\" %}\"  download class=\"btn btn-success btn-sm\"><span class=\"glyphicon glyphicon-download-alt\"></span> </a>"
        showimage = "<div class=\"col-md-4\"><div class=\"thumbnail\"><img src=\" {% static \""+newpath+"\" %}\" alt = "+filename+" >"+filename+"  "+downloadButton+"  "+viewbutton+"</div></div>"
        response = response +showimage
    response = response + "</div>{% endblock %}"
    file = open("imgapp/templates/imgapp/Showresults_KeyVal.html",'w')
    file.write(response)
    file.close()
    return render_to_response("imgapp/Showresults_KeyVal.html")