from django.urls import path
from . import views

app_name = 'blog'  # here for namespacing of urls.

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.new_post, name='new_post'),
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),



    # and so on for other views...
]
