from django.shortcuts import redirect
from django.contrib import messages
from blog.models import Post
from django.contrib.auth import login
import os
from .forms import UploadFileForm, NewUserForm
from django.views.decorators.csrf import csrf_exempt

from .functions.blslines import plot_balance_sheet, load_json_file
from .functions.quickRatios import plot_quick_ratio
from djangoInt.datapostgres.pull_data import fetch_data, fetch_summary, transactions_history, process_profit_and_loss, fetch_bl_data, process_balance_sheet, generate_transaction_report
from django.views.decorators.csrf import csrf_exempt
from .helpers import fetch_table_name_for_user
from django.http import JsonResponse
from djangoInt.datapostgres.postgres_connection import create_connection
engine = create_connection()
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


import json


def dataserv(request):
    default_start_date = '2023-07-01'
    default_end_date = '2023-07-05'

    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
    else:
        start_date = default_start_date
        end_date = default_end_date
    request.session['start_date'] = start_date
    request.session['end_date'] = end_date

    t_name = fetch_table_name_for_user(request.user)
    df = fetch_data(start_date, end_date, t_name)
    transactions = transactions_history(df)
    dfpl = fetch_summary(df)

    # Call the process_profit_and_loss function
    profit_and_loss_result = process_profit_and_loss(df, start_date=start_date, end_date=end_date)
    profit_and_loss_json = json.dumps(profit_and_loss_result, indent=4)

    context = {
        'transactions': transactions.to_html(),
        'summary': dfpl.to_html(),
        'start_date': start_date,
        'end_date': end_date,
        'profit_and_loss': profit_and_loss_json,  # Add the profit and loss JSON to the context
    }

    return render(request, 'dataserv.html', context)


# def dataprog(request):
#     data = load_json_file(os.path.join('djangoInt', 'jsons', 'ratios.json'))
#
#     plot_balance_sheet(data)
#     plot_quick_ratio(data)
#     return render(request, 'dataprog.html')


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
            messages.success(request, "Registration successful.")
            return redirect("home")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"register_form": form})


from django.http import JsonResponse


def profit_and_loss(request):

    start_date = request.session.get('start_date')
    end_date = request.session.get('end_date')

    # Check if the dates are available
    if start_date is None or end_date is None:
        # Redirect to the dataserv view or show an error
        return redirect('dataserv')  # or handle it differently

    t_name = fetch_table_name_for_user(request.user)
    df = fetch_data(start_date, end_date, t_name)

    # Process the data as needed (modify this part to match your data structure)
    statement = process_profit_and_loss(df, start_date=start_date, end_date=end_date)

    # Prepare the context for the template
    data = {
        'company_name': 'My Company',
        'period': f'{start_date} to {end_date}',
        'statement': statement,
    }
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)
    return render(request, 'profit_and_loss.html', data)


def balance_sheet(request):
    end_date = request.session.get('end_date')  # You can replace this with the desired end date
    table_name = fetch_table_name_for_user(request.user)  # Replace with the appropriate table name
    # Process the data to create the balance sheet
    company_name = 'My Company'  # Replace with your company name
    balance_sheet_result = process_balance_sheet(fetch_bl_data, end_date, table_name, company_name)
    # Calculate total revenue
    total_revenue = sum(item['amount'] for item in balance_sheet_result['revenue'])
    # Calculate total expenses
    total_expenses = sum(item['amount'] for item in balance_sheet_result['expense'])
    # Calculate income summary
    income_summary = total_revenue - total_expenses


    # Prepare the context for the template
    context = {
        'company_name': company_name,
        'end_date': end_date,
        'current_asset': balance_sheet_result['current_asset'],
        'fixed_asset': balance_sheet_result['fixed_asset'],
        'current_liability': balance_sheet_result['current_liability'],
        'long-term_liability': balance_sheet_result['long-term_liability'],
        'equity': balance_sheet_result['equity'],
        'income_summary': income_summary,
    }

    with open('data_bl.json', 'w') as file:
        json.dump(context, file, indent=4)

    return render(request, 'balance_sheet.html', context)
def transaction_report(request):
    start_date = request.session.get('start_date')
    end_date = request.session.get('end_date')

    # Check if the dates are available
    if start_date is None or end_date is None:
        # Redirect to the dataserv view or show an error
        return redirect('dataserv')  # or handle it differently

    t_name = fetch_table_name_for_user(request.user)

    # Generate the report URL using the generate_transaction_report function
    report_url = generate_transaction_report(start_date, end_date, t_name, engine)  # Assuming engine is defined elsewhere

    # Render the template with the report URL
    return render(request, 'transactions.html', {'report_url': report_url})