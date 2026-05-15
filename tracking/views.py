from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FileRecord, DailyWorkSubmission
from .forms import FileRecordForm, DailyWorkSubmissionForm

from .filters import FileRecordFilter

@login_required
def file_list(request):
    files = FileRecord.objects.all().order_by('-created_at')
    if request.user.role != 'HQ_ADMIN':
        if not request.user.branch:
            messages.error(request, "You are not assigned to any branch.")
            return redirect('dashboard')
        if request.user.role == 'BRANCH_MANAGER':
            files = files.filter(branch=request.user.branch)
        else:
            files = files.filter(operator=request.user)
    
    file_filter = FileRecordFilter(request.GET, queryset=files)
    return render(request, 'tracking/file_list.html', {
        'filter': file_filter,
        'files': file_filter.qs
    })

@login_required
def register_file(request):
    if request.user.role == 'HQ_ADMIN':
        messages.error(request, "HQ Admins cannot register files directly. Please use a Branch account.")
        return redirect('file_list')
        
    if request.method == 'POST':
        form = FileRecordForm(request.POST)
        if form.is_valid():
            file_record = form.save(commit=False)
            file_record.branch = request.user.branch
            file_record.operator = request.user
            file_record.save()
            messages.success(request, "File registered successfully.")
            return redirect('file_list')
    else:
        form = FileRecordForm()
    return render(request, 'tracking/file_form.html', {'form': form, 'title': 'Register New File'})

@login_required
def submit_work(request):
    if request.user.role == 'HQ_ADMIN':
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = DailyWorkSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.branch = request.user.branch
            submission.operator = request.user
            submission.save()
            messages.success(request, "Daily work submitted successfully.")
            return redirect('dashboard')
    else:
        form = DailyWorkSubmissionForm()
    return render(request, 'tracking/file_form.html', {'form': form, 'title': 'Submit Daily Work'})

@login_required
def daily_work_list(request):
    submissions = DailyWorkSubmission.objects.all().order_by('-date', '-submitted_at')
    
    if request.user.role != 'HQ_ADMIN':
        if not request.user.branch:
            messages.error(request, "You are not assigned to any branch.")
            return redirect('dashboard')
        submissions = submissions.filter(branch=request.user.branch)
        
    return render(request, 'tracking/daily_work_list.html', {
        'submissions': submissions
    })

@login_required
def edit_work(request, submission_id):
    submission = get_object_or_404(DailyWorkSubmission, id=submission_id)
    
    # HQ Admin or the operator who created it can edit
    if request.user.role != 'HQ_ADMIN' and submission.operator != request.user:
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('daily_work_list')
        
    if request.method == 'POST':
        form = DailyWorkSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Daily work updated successfully.")
            return redirect('daily_work_list')
    else:
        form = DailyWorkSubmissionForm(instance=submission)
        
    return render(request, 'tracking/file_form.html', {'form': form, 'title': 'Edit Daily Work'})

@login_required
def delete_work(request, submission_id):
    submission = get_object_or_404(DailyWorkSubmission, id=submission_id)
    
    if request.user.role != 'HQ_ADMIN':
        messages.error(request, "Only Headquarters Admin can delete submissions.")
        return redirect('daily_work_list')
        
    if request.method == 'POST':
        submission.delete()
        messages.success(request, "Daily work submission deleted successfully.")
        return redirect('daily_work_list')
        
    return render(request, 'tracking/confirm_delete.html', {'object': submission, 'title': 'Delete Submission'})
