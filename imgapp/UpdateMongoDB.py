from pymongo import MongoClient
from .ExtractExif import Extract_Exif
from copy import deepcopy
import pprint
from ImageManagementSystem.settings import MONGO_CONNECTION_URL, MONGO_DATABASE, BASE_DIR
import cv2
import shutil
import os


# Upload metadata of the images to the mongoDB
# Also, apply the object detection model to detect the objects and get the bbox coordinates 
# Upload these bbox coordinates with the image's metadata
def update_Mongo(DataSetName, ImageType, DirectoryPath, Utils_Object, timestamp, userID) :
    """
    Upload files to mongodb
    """

    # extract exif data
    Ext_Exif = Extract_Exif()
    Exif_All = Ext_Exif.Extract_MetaData(DirectoryPath)

    # get reference to mongo client
    client = MongoClient(MONGO_CONNECTION_URL)
    db = client[MONGO_DATABASE]
    # print(userID)
    Exif_col = db[str(userID)]

    # Upload timestamps and dataset name 
    loginCOL = db['login']
    loginCOL.insert_one({ "time" : timestamp , "userID" : userID , "dataset" : str(userID)+"_"+DataSetName })


    imgitems = []

    # for all images to be uploaded to mongoDB    
    for image in Exif_All.keys() :

        # ignore images already in mongoDB with same timestamp
        if (Exif_col.find_one({'item.File.FileName' : Exif_All[image]['File']['FileName']}) != None) :
            continue
        
        # dict = metadata to single image
        dict = { 'item' : Exif_All[image] }
        
        # add the upload timestamp 
        dict['item']['File'].update({'TimeStamp' : timestamp})
        
        # if the image in an aerial image,
        # add the object's bbox coordinates to the metadata of that image 
        if(ImageType=="aerial"):
            sourcefile = dict['item']['SourceFile']
            img=cv2.imread(sourcefile)
            detections = Utils_Object.get_boundingBox(img)
            
            objects ={'Objects' : {}}

            # add the bbox coordinates 
            for det in detections :
                if (det[1] not in objects['Objects'].keys()) :
                    objects['Objects'].update({ det[1] : [det[0]] })
                else :
                    objects['Objects'][det[1]].append(det[0])
            dict['item'].update(objects)
         
        imgitems.append(dict)
    
    # upload all the image's metadata
    Exif_col.insert_many(imgitems)


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
        dataset_path = os.path.join(BASE_DIR+'/data',dataset_name)
        if (os.path.exists(dataset_path)):
            shutil.rmtree(dataset_path)
    
    # drop collection 
    Col.drop()

    # delete docs from upload records table
    LoginCOL.delete_many({'userID' : userID, 'time' : {"$exists" : True}})
    
    return 0




if __name__=='__main__' :
    items = update_Mongo('')    
