import os
import re

template_dir = r"c:\Users\hp\Pictures\Digital File Tracking\templates"

translations = {
    "Dashboard": "Dashboard",
    "Admin Panel": "Admin Panel",
    "Branches": "Branches",
    "Audit Logs": "Audit Logs",
    "File Records": "File Records",
    "Reports": "Reports",
    "Logout": "Logout",
    "Login": "Login",
    "Username": "Username",
    "Password": "Password",
    "TOTAL DIGITIZED": "Total Files Digitized",
    "TOTAL PAGES": "Total Pages Scanned",
    "Today's Progress": "Today's Progress",
    "ACTIVE BRANCHES": "Active Branches",
    "OVERALL COMPLETION": "Completion Rate",
    "Branch Performance Summary": "Branch Performance Summary",
    "Branch": "Branch",
    "Total Digitized": "Total Digitized",
    "Today's Work": "Today's Work",
    "Daily Target": "Daily Target",
    "Total Target": "Total Target",
    "Performance (Today)": "Performance (Today)",
    "Performance (Overall)": "Performance (Overall)",
    "Status": "Status",
    "Active Today": "Active Today",
    "Inactive Today": "Inactive Today",
    "Daily Digitization (Last 7 Days)": "Daily Digitization (Last 7 Days)",
    "Volume Distribution": "Volume Distribution",
    "Monthly Performance": "Monthly Performance",
    "Recent Audit Activity": "Recent Audit Activity",
    "Branch Name": "Branch Name",
    "Total Pages": "Total Pages",
    "Daily Avg": "Daily Avg",
    "Target (Period)": "Target (Period)",
    "Full Project Goal": "Full Project Goal",
    "Performance %": "Performance %",
    "Filter Reports": "Filter Reports",
    "Start Date": "Start Date",
    "End Date": "End Date",
    "Apply Filter": "Apply Filter",
    "Export": "Export",
    "Notifications": "Notifications",
    "Mark all as read": "Mark all as read",
    "View all notifications": "View all notifications",
    "Profile": "Profile",
    "Settings": "Settings",
    "Users": "Users",
    "Add New Submission": "Add New Submission",
    "Date": "Date",
    "Files Digitized": "Files Digitized",
    "Pages Scanned": "Pages Scanned",
    "Operator": "Operator",
    "Problems / Solutions": "Problems / Solutions",
    "Comments": "Comments",
    "Submit Work": "Submit Work",
}

for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Wrap translations
            for original in translations.keys():
                # Avoid double-wrapping
                # This is a simple check: if it's already inside {% trans ... %} or contains {% trans
                # We use a regex to match the exact string not surrounded by {% trans %}
                pattern = re.compile(r'(?<!\{% trans ")(?<!\{% trans \')\b' + re.escape(original) + r'\b(?!" %})(?!\' %})')
                content = pattern.sub(f'{{% trans "{original}" %}}', content)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Processed {filepath}")
