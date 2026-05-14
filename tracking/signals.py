from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FileRecord, DailyWorkSubmission, AuditLog, Notification
from core.middleware import get_client_ip

@receiver(post_save, sender=FileRecord)
def log_file_record_save(sender, instance, created, **kwargs):
    action = "Created" if created else "Updated"
    details = f"File {instance.file_id} ({instance.file_name}) was {action.lower()}."
    AuditLog.objects.create(
        user=instance.operator,
        action=f"File {action}",
        details=details,
        ip_address=get_client_ip()
    )

@receiver(post_save, sender=DailyWorkSubmission)
def log_work_submission(sender, instance, created, **kwargs):
    if created:
        details = f"Operator {instance.operator.username} submitted {instance.files_digitized_count} files for {instance.date}."
        AuditLog.objects.create(
            user=instance.operator,
            action="Work Submission",
            details=details,
            ip_address=get_client_ip()
        )
        
        # Create notification
        Notification.objects.create(
            title="New Work Submission",
            message=f"{instance.branch.name}: {instance.files_digitized_count} files digitized by {instance.operator.username}.",
            level='SUCCESS',
            branch=instance.branch
        )
