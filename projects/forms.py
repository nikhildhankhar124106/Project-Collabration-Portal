from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from .models import Project, Task, Comment, File, ProjectMembership


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects"""
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your project...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'assignees']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the task...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'assignees': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
        }
    
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limit assignees to project members only
        if project:
            self.fields['assignees'].queryset = project.members.all()
            self.fields['assignees'].help_text = f'Select up to {settings.MAX_TASK_ASSIGNEES} members'
    
    def clean_assignees(self):
        assignees = self.cleaned_data.get('assignees')
        max_assignees = getattr(settings, 'MAX_TASK_ASSIGNEES', 5)
        
        if assignees and len(assignees) > max_assignees:
            raise forms.ValidationError(
                f'You can assign this task to at most {max_assignees} members.'
            )
        
        return assignees


class CommentForm(forms.ModelForm):
    """Form for adding comments"""
    
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment... (use @username to mention someone)',
                'id': 'comment-text'
            }),
        }
        labels = {
            'text': ''
        }


class FileUploadForm(forms.ModelForm):
    """Form for uploading files"""
    
    class Meta:
        model = File
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_exts = ', '.join(settings.ALLOWED_FILE_EXTENSIONS)
        max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        self.fields['file'].help_text = f'Allowed types: {allowed_exts}. Max size: {max_size_mb}MB'


class AddMemberForm(forms.Form):
    """Form for adding members to a project"""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Select User'
    )
    
    role = forms.ChoiceField(
        choices=ProjectMembership.ROLE_CHOICES[1:],  # Exclude 'owner'
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='viewer'
    )
    
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Exclude users who are already members
        if project:
            existing_member_ids = project.members.values_list('id', flat=True)
            self.fields['user'].queryset = User.objects.exclude(id__in=existing_member_ids)


class ChangeMemberRoleForm(forms.Form):
    """Form for changing a member's role"""
    
    role = forms.ChoiceField(
        choices=ProjectMembership.ROLE_CHOICES[1:],  # Exclude 'owner'
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
