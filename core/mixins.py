from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from projects.models import Project
from projects.permissions import (
    has_project_view_access,
    has_project_edit_access,
    is_project_owner
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
            if not has_project_view_access(request.user, project):
                raise PermissionDenied("You must be a project member to view this page.")
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
                raise PermissionDenied("You must be a project owner or editor to perform this action.")
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
                raise PermissionDenied("You must be the project owner to perform this action.")
        return super().dispatch(request, *args, **kwargs)
