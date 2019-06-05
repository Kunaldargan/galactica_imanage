from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import datetime
import os
from .UpdateMongoDB import update_Mongo
from .MongoQuery import MongoQuery
from .utils import Utils
import shutil
import ast
from ImageManagementSystem.settings import BASE_DIR

Utils_Object = Utils()
DATAPATH = os.path.join(BASE_DIR,'data')
STATICPATH = BASE_DIR+'/imgapp/static'

if not os.path.exists(STATICPATH):
	os.mkdir(STATICPATH)

def Home(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    return render(request,"imgapp/home.html", {})

def Form(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    return render(request, "imgapp/upload.html", {})

def Upload(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    file_list = request.FILES.getlist("files")
    dataset = request.POST['dataset']
    imagetype = request.POST['imagetype']
    path_dataset = os.path.join(DATAPATH,dataset)
    path_imagetype = os.path.join(path_dataset,imagetype)
    for count, x in enumerate(file_list):
        # print(type(x)) # class object of django image type
        def process(f):
            timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))
            if not os.path.exists(path_dataset) :
                os.mkdir(path_dataset)
            if not os.path.exists(path_imagetype) :
                os.mkdir(path_imagetype)
            with open(path_imagetype+'/'+'('+timestamp+')'+ str(x), 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
        process(x)

    update_Mongo(dataset,imagetype,path_imagetype)
    return HttpResponseRedirect(reverse('updated'))

def UpdatedMongo(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    return render(request, "imgapp/DatabaseUpdated.html", {})
    
def QueryMongo(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    return render(request, "imgapp/QueryDatabase.html", {})

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
    imagenames = QueryMongo.Find_Key_Val(query_dict)
    result = os.path.join(STATICPATH,'imgapp') 
    if os.path.exists(result) :
        shutil.rmtree(result)    
    os.mkdir(result)
    return Showresults_keyValue(imagenames,result)

def QueryObject(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    return render(request,"imgapp/QueryObject.html")

def RemoveSpaces(object) :
    newObj = ""
    for i in object :
        if (i!=" "):
            newObj = newObj+i
    return newObj

def QueryObjectResult(request) :
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('loginform'))
    queryval = request.POST['queryvalue']
    objects = []
    queryval = queryval.split(',')
    for object in queryval :
        obj = RemoveSpaces(object) 
        objects.append(obj)
    QueryMongo = MongoQuery()
    imageids = QueryMongo.FindObjects(objects)
    result = os.path.join(STATICPATH,'imgapp') 
    if os.path.exists(result) :
        shutil.rmtree(result)    
    os.mkdir(result)
    Utils_Object.save_annotatedFile(imageids,objects)
    return Showresults_Objects(result)

# show results for Object queries,modifies the template to show the images required
def Showresults_Objects(result) :
    navigationsBarStyle = "<style>ul{list-style-type: none;margin: 0;padding: 0;overflow: hidden;background-color:grey;}li{float: left;}li a{display: block;color: white;text-align: center;padding: 16px;text-decoration: none;}li a:hover {background-color:  black;}</style>"
    bootstrap = "<!DOCTYPE html><html lang=\"en\"><head><title>iManage App</title><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css\"><script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js\"></script><script src=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js\"></script>"+navigationsBarStyle+"</head>"
    navigationsBar = "<ul><li><a href=\"../home/\">Home</a></li><li><a href=\"../form/\">Upload Images</a></li><li><a href=\"../query/\">Query Images</a></li><li><a href=\"../objectquery/\">Object Query</a></li><li><a href=\"https://www.galactica.ai/\">About</a></li></ul>"
    response = bootstrap+"<body> "+navigationsBar+" <div class=\"container\"><h2>Image Results</h2><div class=\"row\">{% load static %}"
    filenames = os.listdir(result)
    for file in filenames :
        path = os.path.join('imgapp',file)
        showimage = "<div class=\"col-md-4\"><div class=\"thumbnail\"><img src=\" {% static \""+path+"\" %}\" alt = "+file+" style=\"width:100%\"><div class=\"caption\"><p>"+file+"</p></div></div></div>"
        response = response +showimage
    response = response + "</div></div></body>"
    file = open("imgapp/templates/imgapp/Showresults_Objects.html",'w')
    file.write(response)
    file.close()
    return render_to_response("imgapp/Showresults_Objects.html")

# show results for key value queries,modifies the template to show the images required
def Showresults_keyValue(paths,destPath) :
    navigationsBarStyle = "<style>ul{list-style-type: none;margin: 0;padding: 0;overflow: hidden;background-color:grey;}li{float: left;}li a{display: block;color: white;text-align: center;padding: 16px;text-decoration: none;}li a:hover {background-color:  black;}</style>"
    bootstrap = "<!DOCTYPE html><html lang=\"en\"><head><title>iManage App</title><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css\"><script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js\"></script><script src=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js\"></script>"+navigationsBarStyle+"</head>"
    navigationsBar = "<ul><li><a href=\"../home/\">Home</a></li><li><a href=\"../form/\">Upload Images</a></li><li><a href=\"../query/\">Query Images</a></li><li><a href=\"../objectquery/\">Object Query</a></li><li><a href=\"https://www.galactica.ai/\">About</a></li></ul>"
    response = bootstrap+"<body> "+navigationsBar+" <div class=\"container\"><h2>Image Results</h2><div class=\"row\">{% load static %}"
    for path in paths :
        path = shutil.copy(path,destPath)
        filename = path[path.rfind('/')+1:]
        newpath = os.path.join('imgapp',filename)
        showimage = "<div class=\"col-md-4\"><div class=\"thumbnail\"><img src=\" {% static \""+newpath+"\" %}\" alt = "+filename+" style=\"width:100%\"><div class=\"caption\"><p>"+filename+"</p></div></div></div>"
        response = response +showimage
    response = response + "</div></div></body>"
    file = open("imgapp/templates/imgapp/Showresults_KeyVal.html",'w')
    file.write(response)
    file.close()
    return render_to_response("imgapp/Showresults_KeyVal.html")
