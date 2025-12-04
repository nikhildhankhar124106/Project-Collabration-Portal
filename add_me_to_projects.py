"""
Script to add a user as a member to all projects they don't own.
This fixes the 403 Forbidden errors.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collab_portal.settings')
django.setup()

from django.contrib.auth.models import User
from projects.models import Project, ProjectMembership

# Get the current user (change this to your username)
username = 'nikhildhankhad'  # Corrected username

try:
    user = User.objects.get(username=username)
    print(f"✅ Found user: {user.username}")
    
    # Get all projects
    all_projects = Project.objects.all()
    print(f"\n📊 Total projects: {all_projects.count()}")
    
    # Add user as editor to all projects they don't own
    added_count = 0
    for project in all_projects:
        # Skip if user is the owner
        if project.owner == user:
            print(f"⏭️  Skipping '{project.name}' - you are the owner")
            continue
        
        # Check if already a member
        existing = ProjectMembership.objects.filter(project=project, user=user).first()
        if existing:
            print(f"ℹ️  Already a member of '{project.name}' as {existing.get_role_display()}")
            continue
        
        # Add as editor
        ProjectMembership.objects.create(
            project=project,
            user=user,
            role='editor'
        )
        added_count += 1
        print(f"✅ Added as Editor to '{project.name}'")
    
    print(f"\n🎉 Done! Added to {added_count} new project(s)")
    print(f"✅ You should now be able to access all projects!")
    
except User.DoesNotExist:
    print(f"❌ Error: User '{username}' not found!")
    print("\nAvailable users:")
    for u in User.objects.all():
        print(f"  - {u.username}")
