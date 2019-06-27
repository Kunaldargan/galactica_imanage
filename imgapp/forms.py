from django.forms import ModelForm
from django import forms 
from .models import Profile, Objects, Description
from django.contrib.auth.models import User

class UserForm(ModelForm) :
    class Meta:
        model = User
        fields = ('username', 'password', 'email')


class ProfileForm(ModelForm) :
    class Meta:
        model = Profile
        fields = ('company',)


object_choices = [
    ('person','person'),
    ('car','car'),
]

class ObjectsForm(ModelForm) :
    objects = forms.MultipleChoiceField(choices=object_choices)

    class Meta:
        model = Objects
        fields = ['objects']

    def clean_choices(self) :
        choices = self.cleaned_data['objects']
        objects = ''.join(choices)
        return objects 

class DescriptionForm(ModelForm) :
    class Meta:
        model = Description
        fields = ['description',]
