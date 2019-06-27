from django.contrib import admin
from .forms import ObjectsForm, Objects, DescriptionForm,Description
# Register your models here.

class ObjectsAdmin(admin.ModelAdmin):
    form = ObjectsForm

class DescriptionAdmin(admin.ModelAdmin) :
    form = DescriptionForm
    readonly_fields = ['description',]

admin.site.register(Objects,ObjectsAdmin)
admin.site.register(Description, DescriptionAdmin)