from django import forms
from .models import Document
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class UploadFileForm(forms.ModelForm):
    First_Name = forms.CharField(max_length=50, required=True)
    Last_Name = forms.CharField(max_length=50, required=True)
    Email = forms.EmailField(max_length=50, required=False)
    uploaded_file = forms.FileField(required=True)
    class Meta:
        model = Document
        fields = ['First_Name', 'Last_Name', 'Email', 'uploaded_file']



class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        # remove the superuser status
        user.is_superuser = False
        user.is_staff = False  # this field often corresponds to the admin site access
        if commit:
            user.save()
        return user
