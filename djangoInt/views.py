from django.shortcuts import render, redirect
from .forms import UploadFileForm, NewUserForm
from django.core.files.storage import default_storage
from django.contrib import messages
from .models import Document
from blog.models import Post
from django.contrib.auth import login




from .functions.blslines import plot_balance_sheet, load_json_file
from .functions.quickRatios import plot_quick_ratio
import os

def index(request):
    latest_post = Post.objects.order_by('-created_on').first()
    return render(request, 'index.html', {'latest_post': latest_post})

def about_us(request):
    return render(request, 'about_us.html')

def pricing(request):
    return render(request, 'pricing.html')

def seorganizer(request):
    return render(request, 'seorganizer.html')

def taxprep(request):
    return render(request, 'taxprep.html')

def dataserv(request):
    return render(request, 'dataserv.html')

def dataprog(request):
    data = load_json_file(os.path.join('djangoInt', 'jsons', 'ratios.json'))

    plot_balance_sheet(data)
    plot_quick_ratio(data)
    return render(request, 'dataprog.html')

def s_corporation(request):
    return render(request, 's_corporation.html')
def new_bus(request):
    return render(request, 'new_bus.html')
def quickbooks(request):
    return render(request, 'quickbooks.html')




def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # get the instance of Document, but don't save it to the database yet
            doc = form.save(commit=False)

            # capture IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            doc.ip_address = ip

            # now save the instance of Document to the database
            doc.save()

            messages.success(request, 'File has been uploaded successfully!')
            return redirect('upload')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("home")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="registration/register.html", context={"register_form":form})
