import os
import django
import sys

# Add the project root to the sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Branch

woredas = [1, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14]
for w in woredas:
    name = f'ወረዳ {w}'
    Branch.objects.get_or_create(
        name=name, 
        defaults={
            'location': 'Addis Ketema', 
            'region': 'Addis Ababa', 
            'code': f'W-{w:02d}', 
            'status': 'Active'
        }
    )
