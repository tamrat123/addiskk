from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
import urllib.request
import json
from .models import FileRecord, DailyWorkSubmission, AuditLog, Notification
from core.middleware import get_client_ip

def fetch_ip_info(log_id):
    try:
        log = AuditLog.objects.get(id=log_id)
        if log.ip_address and log.ip_address not in ('127.0.0.1', '::1', 'localhost'):
            url = f"http://ip-api.com/json/{log.ip_address}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get('status') == 'success':
                    log.country = data.get('country')
                    log.city = data.get('city')
                    log.isp = data.get('isp')
                    log.save(update_fields=['country', 'city', 'isp'])
    except Exception:
        pass

@receiver(post_save, sender=AuditLog)
def fetch_location_for_auditlog(sender, instance, created, **kwargs):
    if created and instance.ip_address:
        threading.Thread(target=fetch_ip_info, args=(instance.id,)).start()

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
