from pymongo import MongoClient
from pprint import pprint
import json
import ast
from ImageManagementSystem.settings import MONGO_CONNECTION_URL, MONGO_DATABASE, MONGO_COLLECTION


class MongoQuery :
    client = None
    db = None
    Col = None

    def __init__(self):
        self.client = MongoClient(MONGO_CONNECTION_URL)
        self.db = self.client[MONGO_DATABASE]
        self.Col = self.db[MONGO_COLLECTION]
        return
    
    def find_key(self,queryfield,Config) :
        for key,value in Config.items() :
            if queryfield in value:
                return(key)
        return -1    

    # find objects in coco images
    def FindObjects(self,QueryValue) :
        with open("imgapp/categories.txt",'r') as f:
            Categories_Dict = json.load(f)
        queryDict = {}
        for obj in QueryValue :
            key = self.find_key(obj,Categories_Dict)
            if (key==-1) :
                return {}
            query = 'item.Objects.'+key+'.'+obj 
            queryDict.update({query : {"$exists" : True }})
        cursor = self.Col.find(queryDict)
        data = list(cursor)
        imageids = {}
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
    