from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from .validators import validate_file_size, validate_file_extension


class Project(models.Model):
    """
    Represents a collaboration project.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(User, through='ProjectMembership', related_name='projects')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_member_count(self):
        return self.members.count()
    
    def get_task_count(self):
        return self.tasks.count()


class ProjectMembership(models.Model):
    """
    Through model for Project-User many-to-many relationship with roles.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'user']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"


class Task(models.Model):
    """
    Represents a task within a project.
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True)
    assignees = models.ManyToManyField(User, related_name='assigned_tasks', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """
        Validate that assignees don't exceed the maximum limit.
        """
        max_assignees = getattr(settings, 'MAX_TASK_ASSIGNEES', 5)
        if self.pk and self.assignees.count() > max_assignees:
            raise ValidationError(
                f'You can assign this task to at most {max_assignees} members.'
            )
    
    def get_status_badge_class(self):
        """Return Bootstrap badge class based on status"""
        status_classes = {
            'todo': 'bg-secondary',
            'in_progress': 'bg-primary',
            'done': 'bg-success',
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    def get_priority_badge_class(self):
        """Return Bootstrap badge class based on priority"""
        priority_classes = {
            'low': 'bg-info',
            'medium': 'bg-warning',
            'high': 'bg-danger',
        }
        return priority_classes.get(self.priority, 'bg-secondary')


class Comment(models.Model):
    """
    Represents a comment on a project or task.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        target = self.project or self.task
        return f"Comment by {self.user.username} on {target}"


class File(models.Model):
    """
    Represents a file uploaded to a project or task.
    """
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        validators=[validate_file_size, validate_file_extension]
    )
    original_filename = models.CharField(max_length=255)
    size = models.IntegerField(help_text='File size in bytes')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.original_filename
    
    def save(self, *args, **kwargs):
        """Auto-populate original_filename and size if not set"""
        if not self.original_filename and self.file:
            self.original_filename = self.file.name
        if not self.size and self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)
    
    def get_size_display(self):
        """Return human-readable file size"""
        size_bytes = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class Notification(models.Model):
    """
    Represents a notification for a user.
    """
    TYPE_CHOICES = [
        ('mention', 'Mention'),
        ('task_assigned', 'Task Assigned'),
        ('member_added', 'Member Added'),
        ('comment_added', 'Comment Added'),
        ('file_uploaded', 'File Uploaded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
    
    def get_link(self):
        """Return the URL to the related object"""
        if self.related_task:
            return f'/projects/{self.related_task.project.pk}/tasks/{self.related_task.pk}/'
        elif self.related_project:
            return f'/projects/{self.related_project.pk}/'
        return '/notifications/'


class Activity(models.Model):
    """
    Represents an activity/event in a project for the activity feed.
    """
    ACTION_CHOICES = [
        ('project_created', 'Project Created'),
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('comment_added', 'Comment Added'),
        ('file_uploaded', 'File Uploaded'),
        ('member_added', 'Member Added'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return f"{self.user.username} - {self.action_type} in {self.project.name}"
