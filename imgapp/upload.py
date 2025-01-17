import json
from ExtractExif import Extract_Exif
from pprint import pprint
from pymongo import MongoClient

def make_imgname(imgid) :
    l = len(imgid)
    n = 16 - l
    imgname = ""
    for i in range(0,n) :
        imgname = imgname + "0"
    imgname = imgname + imgid
    return imgname

def getCat_info(category,cat_id) :
    for val in category :
        if (val['id']==cat_id) :
            return val

def ListObjects(annotations_list,category) :
    img_dict = { }
    for i in range(0,len(annotations_list)) :
        imgdata = annotations_list[i]
        imgid = str(imgdata["image_id"])
        imgname = make_imgname(imgid+"_jpg")
        seg = imgdata["segmentation"]
        bbox = imgdata["bbox"]
        area = imgdata["area"]
        cat_id = imgdata["category_id"]
        print(cat_id)
        cat_info = getCat_info(category,cat_id)
        supercatname = cat_info['supercategory']
        catname = cat_info['name']
        val_dict = {
            'bbox' : bbox,
            'area' : area,
            'segmentation' : seg,
        }
        
        if imgname not in img_dict.keys() :
            cat_dict={}
            cat_dict.update( {catname : [val_dict]} )
            super_cat_dict = {}
            super_cat_dict.update( {supercatname : cat_dict} )
            ann_dict = {
                'Objects' : super_cat_dict
            }
            img_dict.update( { imgname : ann_dict } )
        else:
            ann_dict = img_dict[imgname] 
            super_cat_dict = ann_dict['Objects']
            if supercatname not in super_cat_dict.keys() :
                cat_dict={}
                cat_dict.update( {catname : [val_dict]} )
                super_cat_dict.update( {supercatname : cat_dict} )
            else :
                cat_dict = super_cat_dict[supercatname]
                if catname not in cat_dict.keys() :
                    cat_dict.update( {catname : [val_dict]} )
                else :
                    list_valdict = cat_dict[catname]
                    list_valdict.append(val_dict)


            # cat_dict.update( {cat_name : val_dict } )
    return img_dict


with open('/home/galactica/Downloads/annotations/instances_val2017.json') as json_file :
    data = json.load(json_file)
    annotationsList = data["annotations"]
    category = data["categories"]

    # category_dict = {}

    # for cat in category:
    #     key = cat['supercategory']
    #     if key not in category_dict:
    #         category_dict[key]=[cat['name']]
    #     else:
    #         category_dict[key].append(cat['name'])
    # print(category_dict)
    imgdict = ListObjects(annotationsList,category)
    # print("Extracting ...")
    Ext_Exif = Extract_Exif()
    NewExtAll = []
    ExtALL = Ext_Exif.Extract_MetaData('/home/galactica/Downloads/val2017')
    # pprint(ExtALL)
    # print("Extracted!")
    # print("Adding Objects ...")
    for imgname in imgdict.keys() :
        meta = ExtALL[imgname]
        meta.update( imgdict[imgname] )
        dict = { "item" : meta }
        NewExtAll.append(dict)
    # pprint(NewExtAll)
    # print("Objects Added!")
    client = MongoClient("mongodb://127.0.0.1")
    db = client.database
    Col = db.Col
    # ImagetypeName = 'RBG'
    # DatasetName  = 'Coco'
    # Imagetype = { ImagetypeName : NewExtAll}
    # Dataset = {DatasetName:Imagetype}
    # print("Inserting dataset ...")
    # Col.insert_one(Dataset)
    Col.insert_many(NewExtAll)
    # print("Done!")
