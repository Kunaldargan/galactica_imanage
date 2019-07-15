## @package uploadThreadClass
#
# upload the metra data in a separate thread, (not being used in this imanage branch)

import threading
from .UpdateMongoDB import update_Mongo, delete_User_Collection


## Class to update mongoDB 
# 
# thread class 
class updateMongoThread (threading.Thread):

    ## constructor
    # @param self reference to object itself
    # @param imagetype aerial, satelite, general, etc
    # @param timestamp upload timestamp
    # @param userID primary key of the user  
    def __init__(self,imagetype,path_imagetype,timestamp,userID):
        threading.Thread.__init__(self)
        self.imagetype=imagetype
        self.path_imagetype=path_imagetype
        self.timestamp = timestamp
        self.userID = userID

    ## run method
    # @param self reference to the object itself 
    def run(self):
        print("Starting Thread")
        update_Mongo(self.imagetype,self.path_imagetype,self.timestamp,self.userID,False)
        print("Exiting Thread")