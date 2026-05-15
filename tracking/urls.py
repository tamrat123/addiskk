from django.urls import path
from . import views

urlpatterns = [
    path('files/', views.file_list, name='file_list'),
    path('files/register/', views.register_file, name='register_file'),
    path('work/submit/', views.submit_work, name='submit_work'),
    path('work/list/', views.daily_work_list, name='daily_work_list'),
    path('work/<int:submission_id>/edit/', views.edit_work, name='edit_work'),
    path('work/<int:submission_id>/delete/', views.delete_work, name='delete_work'),
]
