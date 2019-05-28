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
STATICPATH = 'imgapp/static'

def Home(request) :
    return render(request,"imgapp/home.html", {})

def Form(request):
    return render(request, "imgapp/upload.html", {})

def Upload(request):
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
    return render(request, "imgapp/DatabaseUpdated.html", {})
    
def QueryMongo(request) :
    return render(request, "imgapp/QueryDatabase.html", {})

def QueryResults(request) :
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
    return HttpResponse(str(imagenames))

def QueryObject(request) :
    return render(request,"imgapp/QueryObject.html")

def RemoveSpaces(object) :
    newObj = ""
    for i in object :
        if (i!=" "):
            newObj = newObj+i
    return newObj

def QueryObjectResult(request) :
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
    response = " <h1>Result Images</h1> <body>  {% load static %}"
    filenames = os.listdir(result)
    for file in filenames :
        path = os.path.join('imgapp',file)
        showimage = " <div style=\"text-align: center\"><img src=\" {% static \""+path+"\" %}\" alt = "+file+" ></div>"
        response = response +showimage
    response = response + "</body>"
    file = open("imgapp/templates/imgapp/Showresults.html",'w')
    file.write(response)
    file.close()
    return render_to_response("imgapp/Showresults.html")

