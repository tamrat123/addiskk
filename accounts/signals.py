from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import os

@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    if sender.name == 'accounts':
        User = get_user_model()
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')
        
        if not User.objects.filter(is_superuser=True).exists():
            print(f"Creating default superuser: {username}")
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
        else:
            print("Superuser already exists.")
