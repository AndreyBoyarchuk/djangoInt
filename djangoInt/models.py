from django.db import models
from django.utils import timezone
import os

class Document(models.Model):
    First_Name = models.CharField(max_length=50, blank=False)  # Made this field required by setting blank=False
    Last_Name = models.CharField(max_length=50, blank=False)  # Made this field required by setting blank=False
    Email = models.EmailField(max_length=50, blank=True)
    uploaded_file = models.FileField(upload_to='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=50, blank=True)

    def __str__(self):
        # Using strftime to format datetime as string
        date_str = self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        return f'{self.First_Name} {self.Last_Name} - {date_str}'

    def save(self, *args, **kwargs):
        if self.uploaded_file:
            # Get original file name
            original_name = os.path.splitext(self.uploaded_file.name)[0]
            extension = os.path.splitext(self.uploaded_file.name)[1]
            new_name = "{}_{}{}".format(self.First_Name + self.Last_Name, original_name, extension)

            # Rename the uploaded file before saving
            self.uploaded_file.name = new_name

        super().save(*args, **kwargs)

