from django import forms
from .models import FileRecord, DailyWorkSubmission

class FileRecordForm(forms.ModelForm):
    class Meta:
        model = FileRecord
        fields = ['file_id', 'file_name', 'description', 'status', 'completion_date']
        widgets = {
            'file_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter File ID...'}),
            'file_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter File Name...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class DailyWorkSubmissionForm(forms.ModelForm):
    class Meta:
        model = DailyWorkSubmission
        fields = ['date', 'files_digitized_count', 'pages_scanned_count', 'problems_encountered', 'solutions_taken', 'comments']
        labels = {
            'date': 'ቀን (Date)',
            'files_digitized_count': 'ስካን የተደረጉ የፋይል ብዛት የቀን ክንውን',
            'pages_scanned_count': 'ስካን የተደረገ የገፅ ብዛት የቀን ክንውን',
            'problems_encountered': 'ያጋጠሙ ችግሮች',
            'solutions_taken': 'የተወሰደ መፍትሄ',
            'comments': 'ተጨማሪ አስተያየት (Comments)',
        }
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'files_digitized_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'pages_scanned_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'problems_encountered': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'solutions_taken': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
