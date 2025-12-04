from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Project, Task, Comment, File, ProjectMembership, Notification, Activity
import re


@receiver(post_save, sender=Project)
def create_project_activity(sender, instance, created, **kwargs):
    """Create activity when a project is created"""
    if created:
        Activity.objects.create(
            project=instance,
            user=instance.owner,
            action_type='project_created',
            description=f'created project "{instance.name}"'
        )


@receiver(post_save, sender=ProjectMembership)
def notify_member_added(sender, instance, created, **kwargs):
    """Create notification when a user is added to a project"""
    if created and instance.user != instance.project.owner:
        Notification.objects.create(
            user=instance.user,
            message=f'You were added to project "{instance.project.name}" as {instance.get_role_display()}',
            notification_type='member_added',
            related_project=instance.project
        )
        
        # Create activity
        Activity.objects.create(
            project=instance.project,
            user=instance.user,
            action_type='member_added',
            description=f'was added to the project as {instance.get_role_display()}'
        )


@receiver(post_save, sender=Task)
def create_task_activity(sender, instance, created, **kwargs):
    """Create activity when a task is created or updated"""
    if created:
        Activity.objects.create(
            project=instance.project,
            user=instance.created_by or instance.project.owner,
            action_type='task_created',
            description=f'created task "{instance.title}"'
        )


@receiver(m2m_changed, sender=Task.assignees.through)
def notify_task_assigned(sender, instance, action, pk_set, **kwargs):
    """Create notification when users are assigned to a task"""
    if action == 'post_add' and pk_set:
        from django.contrib.auth.models import User
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            # Don't notify if the user assigned themselves
            if user != instance.created_by:
                Notification.objects.create(
                    user=user,
                    message=f'You were assigned to task "{instance.title}"',
                    notification_type='task_assigned',
                    related_project=instance.project,
                    related_task=instance
                )


@receiver(post_save, sender=Comment)
def handle_comment_created(sender, instance, created, **kwargs):
    """Handle comment creation: create activity and parse @mentions"""
    if created:
        # Create activity
        project = instance.project or instance.task.project
        target = 'project' if instance.project else 'task'
        Activity.objects.create(
            project=project,
            user=instance.user,
            action_type='comment_added',
            description=f'commented on {target}'
        )
        
        # Parse @mentions and create notifications
        mentions = re.findall(r'@(\w+)', instance.text)
        if mentions:
            from django.contrib.auth.models import User
            from .models import ProjectMembership
            
            # Get unique mentioned usernames
            mentioned_usernames = set(mentions)
            
            for username in mentioned_usernames:
                try:
                    mentioned_user = User.objects.get(username=username)
                    
                    # Check if mentioned user is a project member
                    if ProjectMembership.objects.filter(project=project, user=mentioned_user).exists():
                        # Don't notify the comment author
                        if mentioned_user != instance.user:
                            # Check if notification already exists to avoid duplicates
                            existing = Notification.objects.filter(
                                user=mentioned_user,
                                notification_type='mention',
                                related_project=instance.project,
                                related_task=instance.task,
                                message__contains=instance.user.username
                            ).exists()
                            
                            if not existing:
                                target_name = instance.project.name if instance.project else instance.task.title
                                Notification.objects.create(
                                    user=mentioned_user,
                                    message=f'{instance.user.username} mentioned you in a comment',
                                    notification_type='mention',
                                    related_project=instance.project or instance.task.project,
                                    related_task=instance.task
                                )
                except User.DoesNotExist:
                    # Username doesn't exist, skip
                    continue


@receiver(post_save, sender=File)
def create_file_activity(sender, instance, created, **kwargs):
    """Create activity when a file is uploaded"""
    if created:
        project = instance.project or instance.task.project
        Activity.objects.create(
            project=project,
            user=instance.uploaded_by,
            action_type='file_uploaded',
            description=f'uploaded file "{instance.original_filename}"'
        )
