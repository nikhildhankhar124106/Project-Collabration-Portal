from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from projects.models import Project, ProjectMembership, Task, Comment, File, Notification, Activity
from projects.permissions import (
    is_project_owner, has_project_edit_access, has_project_view_access, get_user_role
)
import io


class ProjectModelTest(TestCase):
    """Test Project model and membership"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='owner', password='testpass123')
        self.user2 = User.objects.create_user(username='editor', password='testpass123')
        self.user3 = User.objects.create_user(username='viewer', password='testpass123')
        
    def test_project_creation_with_owner(self):
        """Test creating a project and adding owner as member"""
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            owner=self.user1
        )
        
        # Add owner as member
        ProjectMembership.objects.create(
            project=project,
            user=self.user1,
            role='owner'
        )
        
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.owner, self.user1)
        self.assertEqual(project.members.count(), 1)
        self.assertTrue(is_project_owner(self.user1, project))
        
    def test_add_members_with_roles(self):
        """Test adding members with different roles"""
        project = Project.objects.create(
            name='Test Project',
            description='Test',
            owner=self.user1
        )
        
        # Add members
        ProjectMembership.objects.create(project=project, user=self.user1, role='owner')
        ProjectMembership.objects.create(project=project, user=self.user2, role='editor')
        ProjectMembership.objects.create(project=project, user=self.user3, role='viewer')
        
        self.assertEqual(project.members.count(), 3)
        self.assertEqual(get_user_role(self.user1, project), 'owner')
        self.assertEqual(get_user_role(self.user2, project), 'editor')
        self.assertEqual(get_user_role(self.user3, project), 'viewer')
        
    def test_member_added_notification(self):
        """Test that notification is created when member is added"""
        project = Project.objects.create(
            name='Test Project',
            description='Test',
            owner=self.user1
        )
        
        # Add owner (no notification for owner)
        ProjectMembership.objects.create(project=project, user=self.user1, role='owner')
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 0)
        
        # Add editor (should create notification)
        ProjectMembership.objects.create(project=project, user=self.user2, role='editor')
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)
        notification = Notification.objects.get(user=self.user2)
        self.assertEqual(notification.notification_type, 'member_added')


class TaskModelTest(TestCase):
    """Test Task model and assignee management"""
    
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.user3 = User.objects.create_user(username='user3', password='testpass123')
        self.user4 = User.objects.create_user(username='user4', password='testpass123')
        self.user5 = User.objects.create_user(username='user5', password='testpass123')
        self.user6 = User.objects.create_user(username='user6', password='testpass123')
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            owner=self.owner
        )
        
        # Add members
        for user in [self.owner, self.user1, self.user2, self.user3, self.user4, self.user5, self.user6]:
            ProjectMembership.objects.create(project=self.project, user=user, role='editor')
    
    def test_task_creation_and_assignment(self):
        """Test creating task and assigning members"""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='Test Description',
            created_by=self.owner
        )
        
        task.assignees.add(self.user1, self.user2)
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.assignees.count(), 2)
        self.assertIn(self.user1, task.assignees.all())
        
    def test_max_assignees_limit(self):
        """Test that max assignees limit is enforced"""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            created_by=self.owner
        )
        
        # Add max allowed assignees (5)
        task.assignees.add(self.user1, self.user2, self.user3, self.user4, self.user5)
        self.assertEqual(task.assignees.count(), 5)
        
        # Try to add one more (should fail validation)
        task.assignees.add(self.user6)
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            task.clean()
    
    def test_task_assignment_notification(self):
        """Test that notification is created when user is assigned to task"""
        task = Task.objects.create(
            project=self.project,
            title='Test Task',
            created_by=self.owner
        )
        
        task.assignees.add(self.user1)
        
        # Check notification was created
        self.assertEqual(Notification.objects.filter(user=self.user1, notification_type='task_assigned').count(), 1)


class CommentModelTest(TestCase):
    """Test Comment model and validation"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            owner=self.user
        )
        self.task = Task.objects.create(
            project=self.project,
            title='Test Task',
            created_by=self.user
        )
    
    def test_comment_on_project(self):
        """Test creating comment linked to project"""
        comment = Comment.objects.create(
            user=self.user,
            text='Test comment on project',
            project=self.project
        )
        
        self.assertEqual(comment.project, self.project)
        self.assertIsNone(comment.task)
        
    def test_comment_on_task(self):
        """Test creating comment linked to task"""
        comment = Comment.objects.create(
            user=self.user,
            text='Test comment on task',
            task=self.task
        )
        
        self.assertEqual(comment.task, self.task)
        self.assertIsNone(comment.project)
    
    def test_comment_validation_both_or_neither(self):
        """Test that comment must be linked to either project OR task"""
        from django.core.exceptions import ValidationError
        
        # Test with both
        comment = Comment(
            user=self.user,
            text='Test',
            project=self.project,
            task=self.task
        )
        with self.assertRaises(ValidationError):
            comment.clean()
        
        # Test with neither
        comment = Comment(
            user=self.user,
            text='Test'
        )
        with self.assertRaises(ValidationError):
            comment.clean()


class MentionNotificationTest(TestCase):
    """Test @mention functionality and notification creation"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='testpass123')
        self.user2 = User.objects.create_user(username='bob', password='testpass123')
        self.user3 = User.objects.create_user(username='charlie', password='testpass123')
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            owner=self.user1
        )
        
        # Add members
        ProjectMembership.objects.create(project=self.project, user=self.user1, role='owner')
        ProjectMembership.objects.create(project=self.project, user=self.user2, role='editor')
        # user3 is NOT a member
    
    def test_mention_creates_notification(self):
        """Test that @mention creates notification for mentioned user"""
        comment = Comment.objects.create(
            user=self.user1,
            text='Hey @bob, check this out!',
            project=self.project
        )
        
        # Check notification was created for bob
        notifications = Notification.objects.filter(user=self.user2, notification_type='mention')
        self.assertEqual(notifications.count(), 1)
        self.assertIn('alice', notifications.first().message)
    
    def test_mention_non_member_no_notification(self):
        """Test that mentioning non-member doesn't create notification"""
        comment = Comment.objects.create(
            user=self.user1,
            text='Hey @charlie, check this out!',
            project=self.project
        )
        
        # No notification for charlie (not a member)
        self.assertEqual(Notification.objects.filter(user=self.user3).count(), 0)
    
    def test_self_mention_no_notification(self):
        """Test that mentioning yourself doesn't create notification"""
        comment = Comment.objects.create(
            user=self.user1,
            text='Reminder to @alice: finish this',
            project=self.project
        )
        
        # No notification for self-mention
        self.assertEqual(Notification.objects.filter(user=self.user1, notification_type='mention').count(), 0)


class FileUploadTest(TestCase):
    """Test file upload validation"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            owner=self.user
        )
    
    def test_valid_file_upload(self):
        """Test uploading a valid file"""
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile('test.pdf', file_content, content_type='application/pdf')
        
        file_obj = File.objects.create(
            uploaded_by=self.user,
            project=self.project,
            file=uploaded_file,
            original_filename='test.pdf',
            size=len(file_content)
        )
        
        self.assertEqual(file_obj.original_filename, 'test.pdf')
        self.assertEqual(file_obj.size, len(file_content))
    
    def test_invalid_file_extension(self):
        """Test that invalid file extensions are rejected"""
        from django.core.exceptions import ValidationError
        from projects.validators import validate_file_extension
        
        file_content = b'Malicious content'
        uploaded_file = SimpleUploadedFile('malware.exe', file_content, content_type='application/exe')
        
        with self.assertRaises(ValidationError):
            validate_file_extension(uploaded_file)
    
    def test_oversized_file(self):
        """Test that files exceeding size limit are rejected"""
        from django.core.exceptions import ValidationError
        from projects.validators import validate_file_size
        
        # Create a file larger than 5MB
        large_content = b'x' * (6 * 1024 * 1024)  # 6MB
        uploaded_file = SimpleUploadedFile('large.pdf', large_content, content_type='application/pdf')
        
        with self.assertRaises(ValidationError):
            validate_file_size(uploaded_file)


class PermissionTest(TestCase):
    """Test permission enforcement"""
    
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.editor = User.objects.create_user(username='editor', password='testpass123')
        self.viewer = User.objects.create_user(username='viewer', password='testpass123')
        self.outsider = User.objects.create_user(username='outsider', password='testpass123')
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            owner=self.owner
        )
        
        ProjectMembership.objects.create(project=self.project, user=self.owner, role='owner')
        ProjectMembership.objects.create(project=self.project, user=self.editor, role='editor')
        ProjectMembership.objects.create(project=self.project, user=self.viewer, role='viewer')
        
        self.client = Client()
    
    def test_owner_permissions(self):
        """Test that owner has full permissions"""
        self.assertTrue(is_project_owner(self.owner, self.project))
        self.assertTrue(has_project_edit_access(self.owner, self.project))
        self.assertTrue(has_project_view_access(self.owner, self.project))
    
    def test_editor_permissions(self):
        """Test that editor can edit but not manage"""
        self.assertFalse(is_project_owner(self.editor, self.project))
        self.assertTrue(has_project_edit_access(self.editor, self.project))
        self.assertTrue(has_project_view_access(self.editor, self.project))
    
    def test_viewer_permissions(self):
        """Test that viewer can only view"""
        self.assertFalse(is_project_owner(self.viewer, self.project))
        self.assertFalse(has_project_edit_access(self.viewer, self.project))
        self.assertTrue(has_project_view_access(self.viewer, self.project))
    
    def test_outsider_no_permissions(self):
        """Test that non-member has no permissions"""
        self.assertFalse(is_project_owner(self.outsider, self.project))
        self.assertFalse(has_project_edit_access(self.outsider, self.project))
        self.assertFalse(has_project_view_access(self.outsider, self.project))
    
    def test_viewer_cannot_create_task(self):
        """Test that viewer cannot create tasks"""
        self.client.login(username='viewer', password='testpass123')
        response = self.client.get(reverse('task_create', kwargs={'project_pk': self.project.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden


class AuthenticationTest(TestCase):
    """Test authentication error messages"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='correctpass')
    
    def test_invalid_login(self):
        """Test login with invalid credentials shows error"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        # Should show error message
        self.assertContains(response, 'Invalid username or password', status_code=200)
    
    def test_duplicate_username_registration(self):
        """Test registration with existing username shows error"""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',  # Already exists
            'email': 'new@test.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        
        # Should show error about username being taken
        self.assertContains(response, 'already taken', status_code=200)
    
    def test_password_mismatch_registration(self):
        """Test registration with mismatched passwords shows error"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'password123',
            'password2': 'different123'
        })
        
        # Should show password mismatch error
        self.assertContains(response, 'do not match', status_code=200)


class NotificationTest(TestCase):
    """Test notification system"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            owner=self.user
        )
    
    def test_notification_mark_as_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            user=self.user,
            message='Test notification',
            notification_type='mention',
            related_project=self.project
        )
        
        self.assertFalse(notification.is_read)
        
        notification.is_read = True
        notification.save()
        
        self.assertTrue(notification.is_read)
    
    def test_unread_notification_count(self):
        """Test getting unread notification count"""
        # Create 3 notifications, mark 1 as read
        for i in range(3):
            Notification.objects.create(
                user=self.user,
                message=f'Notification {i}',
                notification_type='mention',
                related_project=self.project
            )
        
        # Mark one as read
        Notification.objects.first().is_read = True
        Notification.objects.first().save()
        
        unread_count = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread_count, 2)
