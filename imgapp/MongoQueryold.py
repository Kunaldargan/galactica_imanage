from pymongo import MongoClient
from pprint import pprint


def Check_Query_Key_Value(data,Key,val) :
    if (not isinstance(val,dict)) :
        if (isinstance(data,dict)) :
            for datakey in data :
                strdata = ""
                if (isinstance(data[datakey],str)==False) :
                    strdata=str(data[datakey])
                else:
                    strdata = data[datakey]
                # print(strdata)
                if (datakey==Key and strdata==val) :
                    # print("Yes ",datakey," ",Key)
                    return True
                elif (isinstance(data[datakey],dict)) :
                    var = Check_Query_Key_Value(data[datakey],Key,val)
                    if (var == True) :
                        return True
        elif(isinstance(data,type(val)) and val==data) :
            return True
        else :
            return False



def FindImages(DataSetname,ImageType,QueryField,QueryValue) :
    client = MongoClient("mongodb://Udayaan:21192119@cluster0-shard-00-00-cas9p.mongodb.net:27017,cluster0-shard-00-01-cas9p.mongodb.net:27017,cluster0-shard-00-02-cas9p.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")
    db = client.AerialDB
    Col = db.Col
    DataSet = Col.find_one({DataSetname : {'$exists': True}})
    if (DataSet == None) :
        return ("Dataset : "+DataSetname,0)
    else :
        ImgTypeDict = DataSet[DataSetname]
        # if not ImageType in ImgTypeDict.keys() :
        #     return ("Image Type : "+ImageType,0)
        Images_Data_Dict = ImgTypeDict[ImageType]
        imageNames = []
        for images in Images_Data_Dict :
            if (Check_Query_Key_Value(Images_Data_Dict[images],QueryField,QueryValue)==True) :
                Imagedict = Images_Data_Dict[images]
                imageNames.append(Imagedict['File']['FileName'])
        return (str(imageNames),1)


if __name__ =="__main__" :
    DataSetname  = input("Enter DataSet Name  : ")
    ImageType = input("Enter Image Type : ")
    QueryField = input("Enter the Query Key : ")
    QueryValue = input("Enter the Query Value : ")
    images,status = FindImages(DataSetname,ImageType,QueryField,QueryValue)
    print(images)
        