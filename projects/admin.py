from django.contrib import admin
from .models import Project, ProjectMembership, Task, Comment, File, Notification, Activity


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'role', 'added_at']
    list_filter = ['role', 'added_at']
    search_fields = ['project__name', 'user__username']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']
    filter_horizontal = ['assignees']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_target', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'user__username']
    
    def get_target(self, obj):
        return obj.project or obj.task
    get_target.short_description = 'Target'


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'uploaded_by', 'get_size_display', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['original_filename', 'uploaded_by__username']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'message', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['message', 'user__username']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'action_type', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['description', 'user__username', 'project__name']
