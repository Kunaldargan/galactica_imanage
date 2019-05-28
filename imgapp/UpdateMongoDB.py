from pymongo import MongoClient
from .ExtractExif import Extract_Exif
from copy import deepcopy
import pprint
from ImageManagementSystem.settings import MONGO_CONNECTION_URL, MONGO_DATABASE, MONGO_COLLECTION


def update_Mongo(DataSetName,ImageType,DirectoryPath) :
    Ext_Exif = Extract_Exif()
    Exif_All = Ext_Exif.Extract_MetaData(DirectoryPath)
    client = MongoClient(MONGO_CONNECTION_URL)
    db = client[MONGO_DATABASE]
    Exif_col = db[MONGO_COLLECTION]
    imgitems = []
    for image in Exif_All.keys() :
        if (Exif_col.find_one({'item.File.FileName' : Exif_All[image]['File']['FileName']}) != None) :
            continue
        dict = { 'item' : Exif_All[image] }
        imgitems.append(dict)
    Exif_col.insert_many(imgitems)


if __name__=='__main__' :
    update_Mongo()