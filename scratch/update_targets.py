import os
import django
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\hp\Pictures\Digital File Tracking')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Branch

branches_data = [
    ("ወረዳ 05", "Addis Ababa", 400, 12000),
    ("ወረዳ 12", "Addis Ababa", 400, 12000),
    ("ወረዳ 11", "Addis Ababa", 400, 12000),
    ("ወረዳ 09", "Addis Ababa", 400, 12000),
    ("ወረዳ 08", "Addis Ababa", 400, 12000),
    ("ወረዳ 14", "Addis Ababa", 400, 12000),
    ("ወረዳ 04", "Addis Ababa", 400, 12000),
    ("ወረዳ 01", "Addis Ababa", 400, 12000),
    ("ወረዳ 06", "Addis Ababa", 400, 12000),
    ("ወረዳ 03", "Addis Ababa", 400, 12000),
    ("ወረዳ 13", "Addis Ababa", 400, 12000),
    ("ወረዳ 10", "Addis Ababa", 400, 12000),
]

print("Updating branches...")
for branch_name, region, file_target, page_target in branches_data:
    try:
        branch = Branch.objects.get(name__icontains=branch_name[-2:]) 
        # Attempt to find it by the trailing number (e.g. '5' or '05')
        branch.name = branch_name
        branch.region = region
        branch.daily_target = file_target
        branch.daily_page_target = page_target
        branch.save()
        print(f"Updated {branch_name}")
    except Branch.DoesNotExist:
        # Create it if it doesn't exist
        branch = Branch.objects.create(
            name=branch_name, 
            code=f"W{branch_name.split(' ')[1].zfill(2)}",
            region=region,
            daily_target=file_target,
            daily_page_target=page_target
        )
        print(f"Created {branch_name}")
    except Branch.MultipleObjectsReturned:
        print(f"Multiple branches found for {branch_name}, skipping...")

print("Finished updating branches.")
