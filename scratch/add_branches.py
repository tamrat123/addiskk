import os
import sys
import django

# Add current directory to path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Branch

branches_data = [
    ("ወረዳ 01", 4681),
    ("ወረዳ 03", 10788),
    ("ወረዳ 04", 4514),
    ("ወረዳ 05", 2617),
    ("ወረዳ 06", 7809),
    ("ወረዳ 08", 4830),
    ("ወረዳ 09", 7704),
    ("ወረዳ 10", 1483),
    ("ወረዳ 11", 5121),
    ("ወረዳ 12", 6838),
    ("ወረዳ 13", 6797),
    ("ወረዳ 14", 6747),
]

for name, target in branches_data:
    # Extract number for code
    num = name.split()[-1]
    code = f"W-{num}"
    
    branch, created = Branch.objects.update_or_create(
        name=name,
        defaults={
            'location': 'Addis Ababa',
            'region': 'Addis Ababa',
            'code': code,
            'total_target': target,
            'status': 'Active'
        }
    )
    if created:
        print(f"Created branch code: {code} (Target: {target})")
    else:
        print(f"Updated branch code: {code} (Target: {target})")

print("All branches processed successfully.")
