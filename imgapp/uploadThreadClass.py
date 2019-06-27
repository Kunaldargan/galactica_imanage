import threading
from .UpdateMongoDB import update_Mongo, delete_User_Collection


# Class to update mongoDB 
# *add the object detection inside the run method before updating the database
class UpdateMongo_Thread (threading.Thread):

    # constructor
    def __init__(self,dataset,imagetype,path_imagetype,timestamp,userID):
        threading.Thread.__init__(self)
        self.dataset = dataset
        self.imagetype=imagetype
        self.path_imagetype=path_imagetype
        self.timestamp = timestamp
        self.userID = userID

    # run method
    def run(self):
        print("Starting Thread")
        update_Mongo(self.dataset,self.imagetype,self.path_imagetype,self.timestamp,self.userID,False)
        print("Exiting Thread")