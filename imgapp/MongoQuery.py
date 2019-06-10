from pymongo import MongoClient
from pprint import pprint
import json
import ast
import cv2
from .utils import draw_bbox
from ImageManagementSystem.settings import MONGO_CONNECTION_URL, MONGO_DATABASE, MONGO_COLLECTION


class MongoQuery :
    client = None
    db = None
    Col = None

    def __init__(self):
        self.client = MongoClient(MONGO_CONNECTION_URL)
        self.db = self.client[MONGO_DATABASE]
        self.Col = self.db[MONGO_COLLECTION]
        with open('/home/galactica/Galactica/Production/galactica_imanage/App_Settings.json') as f :
            self.settings = json.load(f)
        with open(self.settings["darknet"]["names"],'r') as c:
            self.classes = [x.rstrip() for x in c.readlines()]
        print(self.classes)

        return

    def find_key(self,queryfield,Config) :
        for key,value in Config.items() :
            if queryfield in value:
                return(key)
        return -1

    def check_aerial(self,QueryValue):
        queryDict = {}
        imgIds = {}
        i = 0;
        for obj in QueryValue:
            if obj in self.classes:
                query = 'item.Objects.'+ obj;
                print(query)
                queryDict.update({query : {"$exists" : True }})
        print(queryDict)
        cursor = self.Col.find(queryDict)
        data = list(cursor)
        for item in data:
            sourcefile = item['item']['SourceFile']
            file = item['item']['File']['FileName']
            #print(item["item"]["Objects"])
            objects = item["item"]["Objects"]

            img=cv2.imread(sourcefile)
            out_img = img
            for obj in objects:
                    for det in objects[obj]:
                        if obj in QueryValue:
                            out_img = draw_bbox(out_img, det, obj)
            print("imgapp/static/imgapp/"+file)
            cv2.imwrite("imgapp/static/imgapp/"+file,out_img)
            imgIds.update({file : "imgapp/"+str(i)+".png"})
            i += 1
        return imgIds



    # find objects in coco images
    def FindObjects(self,QueryValue) :
        with open("imgapp/categories.txt",'r') as f:
            Categories_Dict = json.load(f)
        queryDict = {}
        imageids = {}
        for obj in QueryValue :
            key = self.find_key(obj,Categories_Dict)
            if (key==-1) :
                return(self.check_aerial(QueryValue))
            query = 'item.Objects.'+key+'.'+obj
            queryDict.update({query : {"$exists" : True }})
        cursor = self.Col.find(queryDict)
        data = list(cursor)

        for image in data :
        # especially used for coco; find coco image id and append it to imageids
            def appendID(image) :
                name = image['item']['File']['FileName']
                index = 0
                for s in name :
                    if (s!='0') :
                        break
                    index+=1
            # find id of the coco dataset image
                id = int(name[index:12])
                path = image['item']['SourceFile']
                imageids.update({id : path})
                return
            appendID(image)
        return imageids


    def Find_Key_Val(self,query_dict) :
        with open('imgapp/Config.txt') as Config_file :
            Config = json.load(Config_file)
        queries = {}
        for queryfield in query_dict.keys() :
            key = self.find_key(queryfield,Config)
            if (key == -1) :
                return []
            query = 'item.'+key+'.'+queryfield
            queries.update({ query : query_dict[queryfield]})
        cursor = self.Col.find(queries)
        data = list(cursor)
        imageNames = []
        for image in data :
            imageNames.append(image['item']['SourceFile'])
        return imageNames



if __name__=='__main__' :
    Query = MongoQuery()
    # Query.FindObjects('tv')
    Query.Find_Key_Val({'queryfield' : 'Aperture','queryvalue' : ast.literal_eval('4')})
