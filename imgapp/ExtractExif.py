import exiftool
import sys
import os
import json
import pprint



class Extract_Exif :
    # extensions supported
    img_extensions = ['JPEG','PNG','TIFF','JPG']

    # unwanted items
    unwanted = ["ExifToolVersion","ImageDescription"]

    def __init__(self):
        return

    def list_Files(self,path,is_file_flag):
        if(is_file_flag==True) :
            return [path]
        else :
            listOfFiles = []
            for file in os.listdir(path) :
                i = file.rfind('.')
                extension = file[i+1:]
                extension  = extension.upper()
                if extension in img_extensions :
                    listOfFiles.append(os.path.join(path,file))

            return listOfFiles
    
    def Extract_MetaData(self, path, is_file_flag):
        img_extensions = self.img_extensions
        unwanted = self.unwanted
        listOfFiles = self.list_Files(path,is_file_flag)

        # print(listOfFiles)

        Exif_Result_dict = {}

        with exiftool.ExifTool() as et:
            metadata = et.get_metadata_batch(listOfFiles)

        

        for d in metadata:
            txt = d['File:FileName']
            keys_d = d.keys()
            newkeys = list() #[]
            newdict = dict() #{}
            for s in keys_d :
                if ':' in s:
                    l=s.split(':')
                    
                    if (l[1] in unwanted) :
                        continue
                    
                    if (l[0] not in newdict.keys()) :
                        subdict = {}
                        subdict.update({l[1] : d[s]})
                        newdict.update({l[0] : subdict})
                    else :
                        subdict = newdict[l[0]]
                        subdict.update({l[1] : d[s]})
                        newdict.update({l[0] : subdict})
                    
                else:
                    newdict.update({s : d[s]})
                    

            name = txt.split('.')
            newtxt = ""
            for i in range(0,len(name)) :
                newtxt = newtxt + name[i]
                if (i!=len(name)-1) :
                    newtxt = newtxt + "_"
            Exif_Result_dict.update({newtxt : newdict})
        
        return Exif_Result_dict



    

