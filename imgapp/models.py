from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model) :
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    company = models.CharField(max_length=50)
    
# objects choice model
class Objects(models.Model) :
    objectslist = models.CharField(max_length=4000)


class Description(models.Model) :
    description = models.TextField(help_text="Based in Silicon Valley and Indian Institute of Technology Delhi (IIT-Delhi), we are a group of researchers and entrepreneurs with a fondness for all thing’s deep tech and sci-fi.We aim to solve real world remote sensing problems through Galactica.AI platform by bringing the best minds in research and academia along with strategic industry partnership \n Our R&D team, based out of IIT Delhi is building the core Artificial Intelligence & Machine Learning software infrastructure that can be applied for all the verticals mentioned. Our core software infrastructure is capable of analysing large amounts of video data and doing operations including map generation, orthorectification, photogrammetry, object detection, object tracking, change detection & more. \n Instead of building a one-size-fits-all solution, our team will work closely with customers to customise the Galactica.AI platform to build a solution that works closely with the available infrastructure of the client to deliver very specific needs. Our goal is to reduce barrier to adoption by creating a seamless transition to our platform.")