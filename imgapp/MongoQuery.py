import pymongo
from pprint import pprint
import json
import ast
import cv2
from .utils import draw_bbox
from ImageManagementSystem.settings import MONGO_CONNECTION_URL, MONGO_DATABASE, MONGO_COLLECTION, BASE_DIR
import os

class MongoQuery :
    client = None
    db = None
    Col = None

    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_CONNECTION_URL)
        self.db = self.client[MONGO_DATABASE]
        self.Col = self.db[MONGO_COLLECTION]
        self.timestampsCOl = self.db['timestamps']
        with open(os.path.join(BASE_DIR,'App_Settings.json')) as f :
            self.settings = json.load(f)
        with open(self.settings["darknet"]["names"],'r') as c:
            self.classes = [x.rstrip() for x in c.readlines()]
        # print(self.classes)

        return

    def find_key(self,queryfield,Config) :
        keys=[]
        for key,value in Config.items() :
            if queryfield in value:
                keys.append(key)
        return keys
        

    def custom_search(self,QueryValue,userID,searchtype):
        queryDict = {}
        imgIds = {}
        
        for obj in QueryValue:
            if obj in self.classes:
                query = 'item.Objects.'+ obj;
                queryDict.update({query : { "$exists" : True }})
        
        # search on previously uploaded images only
        if (searchtype=="prev_upload") :

            # find the latest timestamp for the latest upload by current user 
            prev_Timestamp_cursor = self.timestampsCOl.find({'userID' : userID}).sort('_id', pymongo.DESCENDING).limit(1)
            prev_Timestamp_list = list(prev_Timestamp_cursor) 
            # incase no uploads yet, no timestamps in database till now
            # precaution for index error
            if (len(prev_Timestamp_list)==0) :
                return {}
            prev_Timestamp = prev_Timestamp_list[0]['time']

            # search for this timestamp
            queryDict.update( { 'item.File.TimeStamp' : prev_Timestamp } )

        # search on all the images uploaded till now by the user 
        elif(searchtype=="general") :

            # find all the documents for the current user 
            timestamps_cursor = self.timestampsCOl.find({'userID' : userID})

            # or query on mongoDB over all the timestamps 
            queryDict.update( { "$or" : [] } )
            timestamp_docs = list(timestamps_cursor)
            for doc in timestamp_docs :
                queryDict["$or"].append( { "item.File.TimeStamp" : doc['time'] } )

        cursor = self.Col.find(queryDict)
        data = list(cursor)
        
        for item in data:
            sourcefile = item['item']['SourceFile']
            file = item['item']['File']['FileName']
            #print(item["item"]["Objects"])
            img=cv2.imread(sourcefile)
            out_img = img
            objects = item["item"]["Objects"]

            img=cv2.imread(sourcefile)
            out_img = img
            for obj in objects:
                for det in objects[obj] :
                    if obj in QueryValue :
                        out_img = draw_bbox(out_img, det, obj)
            print("imgapp/static/imgapp/"+file)
            cv2.imwrite("imgapp/static/imgapp/"+file,out_img)
            imgIds.update({file : "imgapp/"+file})
            
        return imgIds


   

    # find objects in coco images
    def FindObjectsCOCO(self,QueryValue,Utils_Object) :
        with open("imgapp/categories.txt",'r') as f:
            Categories_Dict = json.load(f)
        queryDict = {}
        imageids = {}
        for obj in QueryValue :
            keys = self.find_key(obj,Categories_Dict)
            if (len(keys)==0) :
                return imageids
            query = 'item.Objects.'+keys[0]+'.'+obj
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
        
        # save the annotated images 
        Utils_Object.save_annotatedFile(imageids,QueryValue)    
        
        return imageids


    def Find_Key_Val(self,query_dict) :
        with open('imgapp/Config.txt') as Config_file :
            Config = json.load(Config_file)
        queries = { "$and" : [] }
        for queryfield in query_dict.keys() :
            keys = self.find_key(queryfield,Config)
            if (len(keys)==0) :
                return []
            else :
                queries["$and"].append( { "$or" : [] } )
                for key in keys :
                    query = 'item.'+key+'.'+queryfield
                    queries["$and"][-1]["$or"].append({ query : query_dict[queryfield] })
        # print(queries)
        cursor = self.Col.find(queries)
        data = list(cursor)
        imageNames = []
        for image in data :
            imageNames.append(image['item']['SourceFile'])

        # print(imageNames)
        return imageNames



if __name__=='__main__' :
    Query = MongoQuery()
    # Query.FindObjects('tv')
    Query.Find_Key_Val({'queryfield' : 'Aperture','queryvalue' : ast.literal_eval('4')})
