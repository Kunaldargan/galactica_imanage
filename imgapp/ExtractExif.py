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

    Config = {}
    
    def __init__(self):
        with open("imgapp/Config.txt") as Config_file :
            self.Config = json.load(Config_file)
        return
    
    def Extract_MetaData(self, Directory):
        img_extensions = self.img_extensions
        unwanted = self.unwanted
        Config = self.Config
        listOfFiles = []
        for file in os.listdir(Directory) :
            i = file.rfind('.')
            extension = file[i+1:]
            extension  = extension.upper()
            if extension in img_extensions :
                listOfFiles.append(os.path.join(Directory,file))

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
                    # Update the Config file
                    if (l[0] not in Config.keys()) :
                        Config.update({l[0]+"" : []})
                    if (l[1] not in Config[l[0]]) :
                        Config[l[0]].append(l[1]+"")
                else:
                    newdict.update({s : d[s]})
                    # Update the Config file
                    Config.update({s+"": []})

            name = txt.split('.')
            newtxt = ""
            for i in range(0,len(name)) :
                newtxt = newtxt + name[i]
                if (i!=len(name)-1) :
                    newtxt = newtxt + "_"
            Exif_Result_dict.update({newtxt : newdict})
        file_object = open("imgapp/Config.txt",'w')
        json.dump(Config,file_object)

        return Exif_Result_dict



    
