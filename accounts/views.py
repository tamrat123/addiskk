from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BranchForm, CustomUserCreationForm
from .models import Branch, CustomUser
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm

@login_required
def add_branch(request):
    if request.user.role != 'HQ_ADMIN':
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New branch added successfully.")
            return redirect('admin_panel')
    else:
        form = BranchForm()
    
    return render(request, 'accounts/add_branch.html', {'form': form, 'title': 'Add New Branch'})

@login_required
def edit_branch(request, pk):
    if request.user.role != 'HQ_ADMIN':
        return redirect('dashboard')
    
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{branch.name}' updated successfully.")
            return redirect('admin_panel')
    else:
        form = BranchForm(instance=branch)
    
    return render(request, 'accounts/add_branch.html', {'form': form, 'title': f'Edit Branch: {branch.name}'})

@login_required
def delete_branch(request, pk):
    if request.user.role != 'HQ_ADMIN':
        return redirect('dashboard')
    
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        branch_name = branch.name
        branch.delete()
        messages.success(request, f"Branch '{branch_name}' has been removed.")
        return redirect('admin_panel')
    
    return render(request, 'accounts/confirm_delete.html', {'object': branch, 'type': 'Branch'})

@login_required
def add_user(request):
    if request.user.role != 'HQ_ADMIN':
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New user created successfully.")
            return redirect('admin_panel')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/add_user.html', {'form': form, 'title': 'Create New User'})

@login_required
def edit_user(request, pk):
    if request.user.role != 'HQ_ADMIN':
        return redirect('dashboard')
    
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        # Simple form for editing basic info and status
        user.username = request.POST.get('username')
        user.role = request.POST.get('role')
        user.status = request.POST.get('status')
        branch_id = request.POST.get('branch')
        if branch_id:
            user.branch = get_object_or_404(Branch, pk=branch_id)
        else:
            user.branch = None
        user.save()
        messages.success(request, f"User '{user.username}' updated successfully.")
        return redirect('admin_panel')
    
    branches = Branch.objects.all()
    return render(request, 'accounts/edit_user.html', {'edit_user': user, 'branches': branches})

@login_required
def reset_password(request, pk):
    if request.user.role != 'HQ_ADMIN':
        return redirect('dashboard')
    
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Password for '{user.username}' has been reset.")
            return redirect('admin_panel')
    else:
        form = SetPasswordForm(user)
    
    return render(request, 'accounts/add_user.html', {'form': form, 'title': f'Reset Password: {user.username}'})
