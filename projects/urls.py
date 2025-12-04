from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Projects
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('<int:pk>/complete/', views.mark_project_completed, name='mark_project_completed'),
    path('<int:pk>/reopen/', views.reopen_project, name='reopen_project'),
    
    # Member management
    path('<int:pk>/members/', views.manage_members, name='manage_members'),
    path('<int:pk>/members/<int:user_id>/remove/', views.remove_member, name='remove_member'),
    path('<int:pk>/members/<int:user_id>/role/', views.change_member_role, name='change_member_role'),
    
    # Tasks
    path('<int:project_pk>/tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('<int:project_pk>/tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('<int:project_pk>/tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('<int:project_pk>/tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    
    # Comments
    path('<int:pk>/comments/add/', views.add_project_comment, name='add_project_comment'),
    path('tasks/<int:pk>/comments/add/', views.add_task_comment, name='add_task_comment'),
    path('comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    
    # Files
    path('<int:pk>/files/upload/', views.upload_project_file, name='upload_project_file'),
    path('tasks/<int:pk>/files/upload/', views.upload_task_file, name='upload_task_file'),
    path('files/<int:pk>/download/', views.download_file, name='download_file'),
    path('files/<int:pk>/delete/', views.delete_file, name='delete_file'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/unread-count/', views.unread_notification_count, name='unread_notification_count'),
    
    # AJAX endpoints
    path('<int:pk>/members/json/', views.get_project_members_json, name='project_members_json'),
]
