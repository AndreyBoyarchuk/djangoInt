
from django.contrib import admin
from django.urls import path, include
from djangoInt import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import register_request


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # add this
    path('', views.index, name='home'),
    path('about_us/', views.about_us, name='about_us'),
    path('pricing/', views.pricing, name='pricing'),
    path('seorganizer/', views.seorganizer, name='seorganizer'),
    path('taxprep/', views.taxprep, name='taxprep'),
    path('dataserv/', views.dataserv, name='dataserv'),
    #path('dataprog/', views.dataprog, name='dataprog'),
    path('s_corporation/', views.s_corporation, name='s_corporation'),
    path('new_bus/', views.new_bus, name='new_bus'),
    path('quickbooks/', views.quickbooks, name='quickbooks'),
    path('upload/', views.upload_file_view, name='upload'),
    path('blog/', include('blog.urls', namespace='blog')),  # Define the namespace here
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path("register", register_request, name="register"),
    path("test", views.test, name="test"),
    path('profitAndLossData', views.profit_and_loss, name='profit_and_loss_data'),
    path('balanceSheetData', views.balance_sheet, name='balance_sheet_data'),
    path('transactions/', views.transaction_report, name='transaction_report'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

