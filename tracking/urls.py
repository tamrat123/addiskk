from django.urls import path
from . import views

urlpatterns = [
    path('files/', views.file_list, name='file_list'),
    path('files/register/', views.register_file, name='register_file'),
    path('work/submit/', views.submit_work, name='submit_work'),
]
