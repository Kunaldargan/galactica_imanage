from django.urls import path
from . import views

urlpatterns = [
    path('home/',views.Home,name="home"),
    path('upload/',views.Upload,name = 'upload'),
    path('form/',views.Form,name = 'form'),
    path('updated/',views.UpdatedMongo,name='updated'),
    path('query/',views.QueryMongo,name='query'),
    path('results/',views.QueryResults,name='results'),
    path('objectquery/',views.QueryObject,name='queryobject'),
    path('objectqueryresults/',views.QueryObjectResult,name='objectresults'),
]