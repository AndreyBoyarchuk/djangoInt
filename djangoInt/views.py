from django.shortcuts import redirect
from django.contrib import messages
from blog.models import Post
from django.contrib.auth import login
import os
from .forms import UploadFileForm, NewUserForm
from django.views.decorators.csrf import csrf_exempt

from .functions.blslines import plot_balance_sheet, load_json_file
from .functions.quickRatios import plot_quick_ratio
from djangoInt.datapostgres.pull_data import fetch_data, fetch_summary,transactions_history
from django.views.decorators.csrf import csrf_exempt
from .helpers import fetch_table_name_for_user
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

from django.shortcuts import render


from django.views.decorators.csrf import csrf_exempt



def test(request):
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        t_name = fetch_table_name_for_user(request.user)

        df = fetch_data(start_date, end_date, t_name)
        dfpl = fetch_summary(df)

        context = {
            'data': df.to_html(),
            'summary': dfpl.to_html(),
            'start_date': start_date,
            'end_date': end_date,
        }
    else:
        context = {
            'data': '',
            'summary': '',
        }

    return render(request, 'test.html', context)
def dataserv(request):
    default_start_date = '2023-07-01'
    default_end_date = '2023-07-05'

    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
    else:
        start_date = default_start_date
        end_date = default_end_date

    t_name = fetch_table_name_for_user(request.user)
    df = fetch_data(start_date, end_date, t_name)
    transactions = transactions_history(df)
    dfpl = fetch_summary(df)

    context = {
        'transactions': transactions.to_html(),
        'summary': dfpl.to_html(),
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'dataserv.html', context)




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
