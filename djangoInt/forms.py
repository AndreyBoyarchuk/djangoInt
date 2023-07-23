from django import forms
from .models import Document

class UploadFileForm(forms.ModelForm):
    First_Name = forms.CharField(max_length=50, required=True)
    Last_Name = forms.CharField(max_length=50, required=True)
    Email = forms.EmailField(max_length=50, required=False)
    uploaded_file = forms.FileField(required=True)
    class Meta:
        model = Document
        fields = ['First_Name', 'Last_Name', 'Email', 'uploaded_file']