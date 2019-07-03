##@package ExtractExif 
#
# extract meta-data from images.
# returns meta-data in json format. 
import exiftool
import sys
import os
import json
import pprint


## Extract_Exif class
#
# extract meta-data of images in json format
class Extract_Exif :
    ## extensions supported
    img_extensions = ['JPEG','PNG','TIFF','JPG']

    ## unwanted items
    unwanted = ["ExifToolVersion","ImageDescription"]

    ## the constructor 
    def __init__(self):
        return

    ## returns path of images in a list
    # @param self reference to object itself
    # @param path path to directory containing images or path to a single file 
    # @param is_file_flag to check if path argument is a path to a directory or a file 
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
    
    ## extract metadata and return it in json format. Also, calls the list_files() function inside.
    # @param self reference to object itself
    # @param path path to directory containing images or path to a single file 
    # @param is_file_flag to check if path argument is a path to a directory or a file 
    def Extract_MetaData(self, path, is_file_flag):
        img_extensions = self.img_extensions
        unwanted = self.unwanted
        listOfFiles = self.list_Files(path,is_file_flag)
        Exif_Result_dict = {}
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata_batch(listOfFiles)

        # parse the metadata and return a recursive dictionary
        for d in metadata:
            txt = d['File:FileName']
            keys_d = d.keys()
            newkeys = list() 
            newdict = dict() 
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



    

