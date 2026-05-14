import polib
import os

po_path = r'c:\Users\hp\Pictures\Digital File Tracking\locale\am\LC_MESSAGES\django.po'
mo_path = r'c:\Users\hp\Pictures\Digital File Tracking\locale\am\LC_MESSAGES\django.mo'

if os.path.exists(po_path):
    po = polib.pofile(po_path)
    po.save_as_mofile(mo_path)
    print(f"Successfully compiled {po_path} to {mo_path}")
else:
    print(f"Error: Could not find {po_path}")
