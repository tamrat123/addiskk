from django.contrib import admin
from .models import Branch, CustomUser

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location', 'created_at')
    search_fields = ('name', 'code')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'branch', 'is_staff')
    list_filter = ('role', 'branch', 'is_staff')
    search_fields = ('username', 'email')
