import os
import django
import sys
import math

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\hp\Pictures\Digital File Tracking')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Branch
from tracking.models import SystemSetting

targets = {
    'ወረዳ 1': 4681,
    'ወረዳ 3': 10788,
    'ወረዳ 4': 4514,
    'ወረዳ 5': 2617,
    'ወረዳ 6': 7809,
    'ወረዳ 8': 4830,
    'ወረዳ 9': 7704,
    'ወረዳ 10': 1483,
    'ወረዳ 11': 5121,
    'ወረዳ 12': 6838,
    'ወረዳ 13': 6797,
    'ወረዳ 14': 6747,
}

total_organization_target = 0

print("Updating branch targets...")
for branch_name, total_target in targets.items():
    daily_target = round(total_target / 30)
    total_organization_target += total_target
    
    # Check if branch exists
    try:
        branch = Branch.objects.get(name=branch_name)
        branch.daily_target = daily_target
        branch.total_target = total_target
        branch.save()
        print(f"Updated {branch_name}: Daily Target = {daily_target}, Total Target = {total_target}")
    except Branch.DoesNotExist:
        # Create it if it doesn't exist
        print(f"Branch '{branch_name}' not found. Creating it...")
        branch = Branch.objects.create(
            name=branch_name, 
            code=f"W{branch_name.split(' ')[1].zfill(2)}",
            daily_target=daily_target,
            total_target=total_target
        )
        print(f"Created {branch_name}: Daily Target = {daily_target}")

# Update System Setting
setting = SystemSetting.load()
setting.organization_target = total_organization_target
setting.save()

print(f"\nUpdated Organization Target to: {total_organization_target}")
