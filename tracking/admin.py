from django.contrib import admin
from .models import FileRecord, DailyWorkSubmission, AuditLog

@admin.register(FileRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ('file_id', 'file_name', 'branch', 'status', 'created_at')
    list_filter = ('status', 'branch', 'created_at')
    search_fields = ('file_id', 'file_name')

@admin.register(DailyWorkSubmission)
class DailyWorkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('branch', 'date', 'files_digitized_count', 'operator')
    list_filter = ('branch', 'date')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'ip_address')
    list_filter = ('action', 'timestamp')
    readonly_fields = ('timestamp', 'user', 'action', 'details', 'ip_address')

    def has_add_permission(self, request):
        return False
