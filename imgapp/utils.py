import os
import cv2
import json
import time
import webcolors
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pycocotools.coco import COCO
import skimage.io as io
from pydarknet import Detector as Det
from pydarknet import Image as darknetImageWrapper
from ImageManagementSystem.settings import BASE_DIR

color_map = {}

def set_color(names_file):
	with open(names_file,'r') as c:
		classes = c.readlines()

	colors = ['Maroon','Red','Yellow','Olive','Lime','Green','Aqua','Teal','Blue','Navy','Purple','Fuchsia'] #Repeat after 12
	n = len(classes)
	m = len(colors)
	j = 0
	print("no. of classes : ", n)
	print("no. of colors : ", m)
	for i in range(n):
		if i > m :
			j = i % m
		color_map[classes[i].rstrip()] = webcolors.name_to_rgb(colors[j])

def get_color(label):
	r = color_map[label].red
	g = color_map[label].green
	b = color_map[label].blue
	return((r,g,b)) #Return color

def draw_bbox(img, bounds, label) :
	x, y, w, h = bounds
	color = get_color(label)
	cv2.rectangle(img, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), color, thickness=2)
	(text_width, text_height) = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, fontScale=1, thickness=1)[0]
	text_offset_x = x
	text_offset_y = y

	# make the coords of the box with a small padding of two pixels
	box_coords = ((int(text_offset_x), int(text_offset_y)), (int(text_offset_x + text_width - 2), int(text_offset_y - text_height - 2)))

	cv2.rectangle(img, box_coords[0], box_coords[1], color, cv2.FILLED)
	cv2.putText(img, label, (int(text_offset_x), int(text_offset_y)), cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255,255,255), thickness=1, lineType=cv2.LINE_AA)
	return(img)

class Utils  :
	coco = None
	Cat = None

	def __init__(self):
		"""
			Initialize : darknet model and coco_api
		"""
		with open(os.path.join(BASE_DIR,'App_Settings.json')) as f :
    			settings = json.load(f)

		self.annfile = settings["coco"]["ann_file"]

		self.coco= COCO(self.annfile)
		self.Cat = self.coco.loadCats(self.coco.getCatIds())
		self.net = Det(bytes(settings["darknet"]["cfg"], encoding="utf-8"),bytes(settings["darknet"]["weights"], encoding="utf-8"), 0, bytes(settings["darknet"]["obj"],encoding="utf-8"))
		self.detection_threshold = settings["darknet"]["threshold"]
		set_color(settings["darknet"]["names"])
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

	def get_boundingBox(self, img) :
		"""
			Wrap around image in darknet format and forward pass
		"""

		detections = []
		dark_frame = darknetImageWrapper(img)
		start_time = time.time()
		results = self.net.detect(dark_frame, thresh=self.detection_threshold);
		del dark_frame
		end_time = time.time()

		print("Elapsed Time:",end_time-start_time)

		for label, score, bounds in results:
			if score > self.detection_threshold:
				label = str(label.decode("utf-8"))
				x,y,w,h = bounds
				#out_img = draw_bbox(img, bounds, label)
				detections.append(((x,y,w,h),label))

		return detections
