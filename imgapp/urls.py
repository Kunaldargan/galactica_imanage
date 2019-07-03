## url patterns inside the imgapp app

from django.urls import path
from . import views

## urlpatterns 
urlpatterns = [
    # path('upload/',views.Upload,name = 'upload'),
    path('form/',views.Form,name = 'form'),
    path('updated/',views.UpdatedMongo,name='updated'),
    path('objectquery/',views.QueryObject,name='queryobject'),
    path('objectqueryresults/',views.QueryObjectResult,name='objectresults'),
    path('deleteCollections/',views.delete,name='dropcollection'),
    path('signup/',views.SignUp_Form,name='signup'),
    path('about/',views.description,name='about'),
]