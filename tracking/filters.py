import django_filters
from django import forms
from .models import FileRecord, Branch

class FileRecordFilter(django_filters.FilterSet):
    file_name = django_filters.CharFilter(
        field_name='file_name', 
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name...'})
    )
    status = django_filters.ChoiceFilter(
        choices=FileRecord.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    branch = django_filters.ModelChoiceFilter(
        queryset=Branch.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = FileRecord
        fields = ['status', 'branch', 'operator']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to operator
        if 'operator' in self.filters:
            self.filters['operator'].field.widget.attrs.update({'class': 'form-select'})
