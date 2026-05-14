from django.db import models
from accounts.models import Branch, CustomUser

class FileRecord(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ARCHIVED', 'Archived'),
    )
    
    file_id = models.CharField(max_length=100, unique=True)
    file_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='file_records')
    operator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='processed_files')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completion_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.file_id} - {self.file_name}"

class DailyWorkSubmission(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    operator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    files_digitized_count = models.PositiveIntegerField(default=0)
    pages_scanned_count = models.PositiveIntegerField(default=0)
    problems_encountered = models.TextField(blank=True)
    solutions_taken = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('branch', 'operator', 'date')

    def __str__(self):
        return f"{self.branch.name} - {self.date} - {self.operator.username}"

class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user.username if self.user else 'System'} - {self.action}"

class Notification(models.Model):
    LEVEL_CHOICES = (
        ('INFO', 'Information'),
        ('SUCCESS', 'Success'),
        ('WARNING', 'Warning'),
        ('DANGER', 'Critical'),
    )
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.title

class SystemSetting(models.Model):
    organization_target = models.PositiveIntegerField(default=50000)
    daily_target_per_branch = models.PositiveIntegerField(default=20)
    backup_frequency = models.CharField(max_length=50, default='Daily')
    alert_threshold_days = models.PositiveIntegerField(default=2)
    
    def save(self, *args, **kwargs):
        self.pk = 1 # Always save to the same record
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
