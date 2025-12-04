from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Q
from django.contrib.auth.models import User
from core.mixins import ProjectMemberRequiredMixin, ProjectEditorRequiredMixin, ProjectOwnerRequiredMixin
from .models import Project, Task, Comment, File, Notification, Activity, ProjectMembership
from .forms import ProjectForm, TaskForm, CommentForm, FileUploadForm, AddMemberForm, ChangeMemberRoleForm
from .permissions import get_user_projects, has_project_edit_access, is_project_owner


class DashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard showing user's projects.
    """
    model = Project
    template_name = 'projects/dashboard.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        return get_user_projects(self.request.user).order_by('-updated_at')


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new project.
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        
        # Add owner as a member with 'owner' role
        ProjectMembership.objects.create(
            project=self.object,
            user=self.request.user,
            role='owner'
        )
        
        messages.success(self.request, f'Project "{self.object.name}" created successfully!')
        return response
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})


class ProjectDetailView(ProjectMemberRequiredMixin, DetailView):
    """
    View project details, tasks, files, comments, and activity.
    """
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Get tasks with filters
        tasks = project.tasks.all()
        status_filter = self.request.GET.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        context['tasks'] = tasks
        context['members'] = project.memberships.select_related('user').all()
        context['files'] = project.files.select_related('uploaded_by').all()[:10]
        context['comments'] = project.comments.select_related('user').all()
        context['activities'] = project.activities.select_related('user').all()[:20]
        context['comment_form'] = CommentForm()
        context['file_form'] = FileUploadForm()
        context['is_owner'] = is_project_owner(self.request.user, project)
        context['can_edit'] = has_project_edit_access(self.request.user, project)
        
        return context


class ProjectUpdateView(ProjectOwnerRequiredMixin, UpdateView):
    """
    Edit project details (owner only).
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(ProjectOwnerRequiredMixin, DeleteView):
    """
    Delete project (owner only).
    """
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, f'Project "{self.object.name}" deleted successfully.')
        return super().form_valid(form)


@login_required
def manage_members(request, pk):
    """
    Manage project members (owner only).
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user is owner
    if not is_project_owner(request.user, project):
        messages.error(request, 'Only the project owner can manage members.')
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        form = AddMemberForm(request.POST, project=project)
        if form.is_valid():
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']
            
            ProjectMembership.objects.create(
                project=project,
                user=user,
                role=role
            )
            
            messages.success(request, f'{user.username} added to project as {role}.')
            return redirect('manage_members', pk=pk)
    else:
        form = AddMemberForm(project=project)
    
    memberships = project.memberships.select_related('user').all()
    
    return render(request, 'projects/manage_members.html', {
        'project': project,
        'form': form,
        'memberships': memberships
    })


@login_required
def remove_member(request, pk, user_id):
    """
    Remove a member from the project (owner only).
    """
    project = get_object_or_404(Project, pk=pk)
    
    if not is_project_owner(request.user, project):
        messages.error(request, 'Only the project owner can remove members.')
        return redirect('project_detail', pk=pk)
    
    user = get_object_or_404(User, pk=user_id)
    
    # Don't allow removing the owner
    if user == project.owner:
        messages.error(request, 'Cannot remove the project owner.')
        return redirect('manage_members', pk=pk)
    
    membership = get_object_or_404(ProjectMembership, project=project, user=user)
    membership.delete()
    
    messages.success(request, f'{user.username} removed from project.')
    return redirect('manage_members', pk=pk)


@login_required
def change_member_role(request, pk, user_id):
    """
    Change a member's role (owner only).
    """
    project = get_object_or_404(Project, pk=pk)
    
    if not is_project_owner(request.user, project):
        messages.error(request, 'Only the project owner can change member roles.')
        return redirect('project_detail', pk=pk)
    
    user = get_object_or_404(User, pk=user_id)
    membership = get_object_or_404(ProjectMembership, project=project, user=user)
    
    # Don't allow changing owner's role
    if user == project.owner:
        messages.error(request, 'Cannot change the project owner\'s role.')
        return redirect('manage_members', pk=pk)
    
    if request.method == 'POST':
        form = ChangeMemberRoleForm(request.POST)
        if form.is_valid():
            membership.role = form.cleaned_data['role']
            membership.save()
            messages.success(request, f'{user.username}\'s role changed to {membership.get_role_display()}.')
            return redirect('manage_members', pk=pk)
    
    return redirect('manage_members', pk=pk)


class TaskCreateView(ProjectEditorRequiredMixin, CreateView):
    """
    Create a new task in a project.
    """
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return kwargs
    
    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Task "{self.object.title}" created successfully!')
        return response
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.kwargs['project_pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context


class TaskDetailView(ProjectMemberRequiredMixin, DetailView):
    """
    View task details.
    """
    model = Task
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        context['project'] = task.project
        context['comments'] = task.comments.select_related('user').all()
        context['files'] = task.files.select_related('uploaded_by').all()
        context['comment_form'] = CommentForm()
        context['file_form'] = FileUploadForm()
        context['can_edit'] = has_project_edit_access(self.request.user, task.project)
        return context


class TaskUpdateView(ProjectEditorRequiredMixin, UpdateView):
    """
    Edit a task.
    """
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.object.project
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('task_detail', kwargs={
            'project_pk': self.object.project.pk,
            'pk': self.object.pk
        })
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        return context


class TaskDeleteView(ProjectEditorRequiredMixin, DeleteView):
    """
    Delete a task.
    """
    model = Task
    template_name = 'projects/task_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.project.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Task "{self.object.title}" deleted successfully.')
        return super().form_valid(form)


@login_required
def add_project_comment(request, pk):
    """
    Add a comment to a project.
    """
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.project = project
            comment.save()
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Error adding comment.')
    
    return redirect('project_detail', pk=pk)


@login_required
def add_task_comment(request, pk):
    """
    Add a comment to a task.
    """
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.task = task
            comment.save()
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Error adding comment.')
    
    return redirect('task_detail', project_pk=task.project.pk, pk=pk)


@login_required
def delete_comment(request, pk):
    """
    Delete a comment (author or project owner only).
    """
    comment = get_object_or_404(Comment, pk=pk)
    project = comment.project or comment.task.project
    
    # Check permissions
    if request.user != comment.user and not is_project_owner(request.user, project):
        messages.error(request, 'You can only delete your own comments.')
        return redirect('project_detail', pk=project.pk)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    
    # Redirect back to the appropriate page
    if comment.project:
        return redirect('project_detail', pk=comment.project.pk)
    else:
        return redirect('task_detail', project_pk=comment.task.project.pk, pk=comment.task.pk)


@login_required
def upload_project_file(request, pk):
    """
    Upload a file to a project.
    """
    project = get_object_or_404(Project, pk=pk)
    
    if not has_project_edit_access(request.user, project):
        messages.error(request, 'You do not have permission to upload files.')
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.uploaded_by = request.user
            file_obj.project = project
            file_obj.save()
            messages.success(request, 'File uploaded successfully!')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect('project_detail', pk=pk)


@login_required
def upload_task_file(request, pk):
    """
    Upload a file to a task.
    """
    task = get_object_or_404(Task, pk=pk)
    
    if not has_project_edit_access(request.user, task.project):
        messages.error(request, 'You do not have permission to upload files.')
        return redirect('task_detail', project_pk=task.project.pk, pk=pk)
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.uploaded_by = request.user
            file_obj.task = task
            file_obj.save()
            messages.success(request, 'File uploaded successfully!')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect('task_detail', project_pk=task.project.pk, pk=pk)


@login_required
def download_file(request, pk):
    """
    Download a file (project members only).
    """
    file_obj = get_object_or_404(File, pk=pk)
    project = file_obj.project or file_obj.task.project
    
    # Check if user is a project member
    if not project.members.filter(pk=request.user.pk).exists():
        messages.error(request, 'You do not have permission to download this file.')
        return redirect('dashboard')
    
    # Serve the file
    response = FileResponse(file_obj.file.open('rb'), as_attachment=True, filename=file_obj.original_filename)
    return response


@login_required
def delete_file(request, pk):
    """
    Delete a file (uploader or project owner only).
    """
    file_obj = get_object_or_404(File, pk=pk)
    project = file_obj.project or file_obj.task.project
    
    # Check permissions
    if request.user != file_obj.uploaded_by and not is_project_owner(request.user, project):
        messages.error(request, 'You can only delete files you uploaded.')
        return redirect('project_detail', pk=project.pk)
    
    if request.method == 'POST':
        file_obj.delete()
        messages.success(request, 'File deleted successfully.')
    
    # Redirect back
    if file_obj.project:
        return redirect('project_detail', pk=file_obj.project.pk)
    else:
        return redirect('task_detail', project_pk=file_obj.task.project.pk, pk=file_obj.task.pk)


class NotificationListView(LoginRequiredMixin, ListView):
    """
    List all notifications for the current user.
    """
    model = Notification
    template_name = 'projects/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@login_required
def mark_notification_read(request, pk):
    """
    Mark a notification as read and redirect to related object.
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    # Redirect to related object
    return redirect(notification.get_link())


@login_required
def unread_notification_count(request):
    """
    AJAX endpoint to get unread notification count.
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def get_project_members_json(request, pk):
    """
    AJAX endpoint to get project members for @mention autocomplete.
    """
    project = get_object_or_404(Project, pk=pk)
    members = project.members.values('id', 'username', 'first_name', 'last_name')
    return JsonResponse(list(members), safe=False)
