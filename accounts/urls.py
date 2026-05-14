from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('branch/add/', views.add_branch, name='add_branch'),
    path('branch/edit/<int:pk>/', views.edit_branch, name='edit_branch'),
    path('branch/delete/<int:pk>/', views.delete_branch, name='delete_branch'),
    path('user/add/', views.add_user, name='add_user'),
    path('user/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('user/reset-password/<int:pk>/', views.reset_password, name='reset_password'),
]
