from django.db import models
from django.contrib.auth.models import AbstractUser

class Branch(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
    )
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    region = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    daily_target = models.PositiveIntegerField(default=20, help_text="Daily File Target")
    total_target = models.PositiveIntegerField(default=600, help_text="Total Project Target")
    daily_page_target = models.PositiveIntegerField(default=100, help_text="Daily Page Target")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Branches"

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('HQ_ADMIN', 'Headquarters Admin'),
        ('BRANCH_MANAGER', 'Branch Manager'),
        ('OPERATOR', 'Operator'),
    )
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OPERATOR')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
