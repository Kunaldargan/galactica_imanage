## @package UpdateMongoDB
# 
# utilities to update documents in MongoDB

from pymongo import MongoClient
from .ExtractExif import Extract_Exif
from copy import deepcopy
import pprint
from galactica_imanage.settings import MONGO_CONNECTION_URL, MONGO_DATABASE, BASE_DIR, DATAPATH
import cv2
import shutil
import os
from .utils import Utils

## Uitls object : instance of the model
Utils_Object = Utils()

## upload file's meta-data to mongoDB
# @param ImageType types include aerial, solar, general, for now the model is run only on aerial images
# @param Path path to the image to be uploaded
# @param timestamp timestamp of the upload 
# @param userID primary key of the user model 
# @param is_file_flag True if path to a file is passed in path argument, path to a directory containing images can also be passed
def update_Mongo(ImageType, Path, timestamp, userID, is_file_flag) :
    
    # extract exif data
    Ext_Exif = Extract_Exif()
    Exif_All = Ext_Exif.Extract_MetaData(Path, is_file_flag)

    # get reference to mongo client
    client = MongoClient(MONGO_CONNECTION_URL)
    db = client[MONGO_DATABASE]
    # print(userID)
    Exif_col = db[str(userID)]

    # Upload timestamps and dataset name 
    loginCOL = db['login']
    timestamp_doc ={}
    if (is_file_flag==True) :
        timestamp_doc = {"time" : timestamp , "userID" : userID , "directory" : os.path.split(Path)[0] , "path" : Path}
    else :
        timestamp_doc = {"time" : timestamp , "userID" : userID , "directory" : Path , "path" : Path}
        
    # if timestamp record doesn't already exist in the loginCOL then upload it to mongoDB
    if (loginCOL.find_one(timestamp_doc)== None) :
        loginCOL.insert_one(timestamp_doc)
    


    imgitems = []

    # for all images to be uploaded to mongoDB    
    for image in Exif_All.keys() :

        # ignore images already in mongoDB with same timestamp
        if (Exif_col.find_one({'item.SourceFile' : Exif_All[image]['SourceFile']}) != None) :
            continue
        
        # dict_item = metadata to single image
        dict_item = { 'item' : Exif_All[image] }
        
        # add the upload timestamp 
        dict_item['item']['File'].update({'TimeStamp' : timestamp})


        # add createdate to EXIF if not already present 
        if ('EXIF' not in dict_item['item'].keys()) :
            dict_item['item'].update({'EXIF' : {}})
            dict_item['item']['EXIF'].update({'CreateDate' : timestamp})
        elif ('CreateDate' not in dict_item['item']['EXIF'].keys()) :
            dict_item['item']['EXIF'].update({'CreateDate' : timestamp})

        
        # if the image in an aerial image,
        # add the object's bbox coordinates to the metadata of that image 
        if(ImageType=="aerial"):
            sourcefile = dict_item['item']['SourceFile']
            img=cv2.imread(sourcefile)
            detections = Utils_Object.get_boundingBox(img)
            
            objects ={'Objects' : {}}

            # add the bbox coordinates 
            for det in detections :
                if (det[1] not in objects['Objects'].keys()) :
                    objects['Objects'].update({ det[1] : [det[0]] })
                else :
                    objects['Objects'][det[1]].append(det[0])
            dict_item['item'].update(objects)
         
        # pprint.pprint(dict_item)
        imgitems.append(dict_item)
    
    if (len(imgitems)==0) :
        return
    
    # upload all the image's metadata
    Exif_col.insert_many(imgitems)

## drop user collection, not functioning with this imanage branch, but given here for reference
# issue: user filebrowser folders are not different 
# @param userID primary key of the user whose complete database has to be deleted
def delete_User_Collection(userID) :
    """
    drop collection for current user 
    """
    
    # get reference to mongo client
    client = MongoClient(MONGO_CONNECTION_URL)
    db = client[MONGO_DATABASE]
    Col = db[str(userID)]

    # get reference to upload tables for this user in mongo
    LoginCOL = db['login']
    all_uploads_cursor = LoginCOL.find({'userID' : userID,'time' : {"$exists" : True}})
    all_uploads = list(all_uploads_cursor)
    
    # if no uploads yet
    if (len(all_uploads)==0) :
        return -1
    # remove all the data files 
    for doc in all_uploads :
        dataset_name = doc['dataset']
        dataset_path = os.path.join(DATAPATH,dataset_name)
        if (os.path.exists(dataset_path)):
            shutil.rmtree(dataset_path)
    
    # drop collection 
    Col.drop()

    # delete docs from upload records table
    LoginCOL.delete_many({'userID' : userID, 'time' : {"$exists" : True}})
    
    return 0


## delete documents from mongoDB, used in the delete method of UserFileBrowserSite class
# @param is_file_flag True if path to a file is passed 
# @param path path to the file or folder to be deleted
# @param userID primary key of the user 
def delete_file_data(is_file_flag, path, userID) :
    
    client = MongoClient(MONGO_CONNECTION_URL)
    db = client[MONGO_DATABASE]
    
    Col = db[str(userID)]

    LoginCOL = db['login']
    
    if (is_file_flag==True) :
        LoginCOL.remove({'path' : path, 'userID' : userID})
        Col.remove({'item.SourceFile' : path})
    else :
        Col.remove({'item.File.Directory' : path})
        LoginCOL.remove({'directory' : path, 'userID' : userID})


if __name__=='__main__' :
    items = update_Mongo('')    
