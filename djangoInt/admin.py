from django.contrib import admin
from .models import Document
from .models import CompanyAuthorization
admin.site.register(Document)
admin.site.register(CompanyAuthorization)