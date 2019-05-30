import os
import numpy as np
import matplotlib.pyplot as plt
from pycocotools.coco import COCO
import skimage.io as io

annfile = "imgapp/instances_val2017.json"

class Utils  :
    coco = None
    Cat = None
    
    def __init__(self):
        self.coco= COCO(annfile)
        self.Cat = self.coco.loadCats(self.coco.getCatIds())
        return

    def save_annotatedFile(self,imgIds,cat_names) :
        catIds = self.coco.getCatIds(catNms=cat_names)
        imagesLoaded = 0
        for img in imgIds.keys() :
            if (imagesLoaded==100) : 
                break
            I = io.imread(imgIds[img])
            plt.imshow(I); plt.axis('off')
            annIds = self.coco.getAnnIds(imgIds=img, catIds=catIds, iscrowd=None)
            anns = self.coco.loadAnns(annIds)
            self.coco.showAnns(anns)
            plt.savefig("imgapp/static/imgapp/"+str(img)+".png",bbox_inches = 'tight',pad_inches=0.0)
            plt.close()
            imagesLoaded+=1
    

