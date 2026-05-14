from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('branches/', views.branch_list_view, name='branch_list'),
    path('reports/', views.reports_view, name='reports'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
]
