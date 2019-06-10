from pymongo import MongoClient
from .ExtractExif import Extract_Exif
from copy import deepcopy
import pprint
from ImageManagementSystem.settings import MONGO_CONNECTION_URL, MONGO_DATABASE, MONGO_COLLECTION
import cv2

def update_Mongo(DataSetName,ImageType,DirectoryPath, Utils_Object) :
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
        # dict = {'item' : {}}
        if(ImageType=="Aerial"):
            # sourcefile = dict['item']['SourceFile']
            # file = dict['item']['File']['FileName']
            # img=cv2.imread(sourcefile)
            detections = Utils_Object.get_boundingBox(img)
            objects ={'Objects' : {}}
            # out_img = img

            for det in detections :
                # out_img = Utils_Object.draw_bbox(out_img,det[0],det[1])
                if (det[1] not in objects['Objects'].keys()) :
                    objects['Objects'].update({ det[1] : [det[0]] })
                else :
                    objects['Objects'][det[1]].append(det[0])
            dict['item'].update(objects)
            # cv2.imwrite("imgapp/static/imgapp/"+file,out_img)

        imgitems.append(dict)
    # return imgitems
    Exif_col.insert_many(imgitems)


if __name__=='__main__' :
    items = update_Mongo('')
    pprint.pprint(item[0])
