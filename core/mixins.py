from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from projects.models import Project, Task
from projects.permissions import (
    has_project_view_access,
    has_project_edit_access,
    is_project_owner,
    has_task_access
)


class ProjectMemberRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require that the user is a member of the project.
    """
    def dispatch(self, request, *args, **kwargs):
        # Get project from URL kwargs
        project_pk = kwargs.get('pk') or kwargs.get('project_pk')
        if project_pk:
            project = get_object_or_404(Project, pk=project_pk)
            
            # Check if this is a task-specific URL
            if 'task' in request.path.lower() and kwargs.get('pk') and project_pk == kwargs.get('project_pk'):
                # This is a task URL, check task-specific permissions
                try:
                    task = Task.objects.get(pk=kwargs.get('pk'))
                    if not has_task_access(request.user, task):
                        return render(request, 'projects/access_denied.html', {
                            'project_name': project.name,
                            'resource_type': 'task',
                            'resource_name': task.title
                        })
                except Task.DoesNotExist:
                    pass
            else:
                # This is a project URL, check project-level permissions
                if not has_project_view_access(request.user, project):
                    # Determine resource type and name
                    resource_type = "project"
                    resource_name = project.name
                    
                    if 'file' in request.path.lower():
                        resource_type = "file"
                    
                    return render(request, 'projects/access_denied.html', {
                        'project_name': project.name,
                        'resource_type': resource_type,
                        'resource_name': resource_name
                    })
        return super().dispatch(request, *args, **kwargs)


class ProjectEditorRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require that the user is an owner or editor of the project.
    """
    def dispatch(self, request, *args, **kwargs):
        project_pk = kwargs.get('pk') or kwargs.get('project_pk')
        if project_pk:
            project = get_object_or_404(Project, pk=project_pk)
            if not has_project_edit_access(request.user, project):
                messages.error(request, f'You do not have permission to edit this project. Only owners and editors can perform this action.')
                return redirect('project_detail', pk=project.pk)
        return super().dispatch(request, *args, **kwargs)


class ProjectOwnerRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require that the user is the owner of the project.
    """
    def dispatch(self, request, *args, **kwargs):
        project_pk = kwargs.get('pk') or kwargs.get('project_pk')
        if project_pk:
            project = get_object_or_404(Project, pk=project_pk)
            if not is_project_owner(request.user, project):
                messages.error(request, f'You do not have permission to perform this action. Only the project owner can do this.')
                return redirect('project_detail', pk=project.pk)
        return super().dispatch(request, *args, **kwargs)
