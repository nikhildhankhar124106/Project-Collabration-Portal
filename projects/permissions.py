from guardian.shortcuts import get_objects_for_user
from .models import ProjectMembership


def get_user_role(user, project):
    """
    Get the user's role in a project.
    Returns the role string ('owner', 'editor', 'viewer') or None if not a member.
    """
    try:
        membership = ProjectMembership.objects.get(project=project, user=user)
        return membership.role
    except ProjectMembership.DoesNotExist:
        return None


def is_project_owner(user, project):
    """
    Check if the user is the owner of the project.
    """
    return project.owner == user


def is_project_member(user, project):
    """
    Check if the user is a member of the project (any role).
    """
    return ProjectMembership.objects.filter(project=project, user=user).exists()


def has_project_view_access(user, project):
    """
    Check if the user can view the project (any member role).
    """
    return is_project_member(user, project)


def has_project_edit_access(user, project):
    """
    Check if the user can edit content in the project (Owner or Editor).
    """
    role = get_user_role(user, project)
    return role in ['owner', 'editor']


def has_project_manage_access(user, project):
    """
    Check if the user can manage the project settings and members (Owner only).
    """
    return is_project_owner(user, project)


def get_user_projects(user):
    """
    Get all projects where the user is a member.
    """
    return user.projects.all()


def can_assign_task(user, project):
    """
    Check if user can assign tasks in the project.
    Only owners and editors can assign tasks.
    """
    return has_project_edit_access(user, project)


def can_manage_members(user, project):
    """
    Check if user can manage project members.
    Only the project owner can manage members.
    """
    return is_project_owner(user, project)
