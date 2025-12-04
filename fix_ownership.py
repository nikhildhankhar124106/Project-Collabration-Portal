import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collab_portal.settings')
django.setup()

from django.contrib.auth.models import User
from projects.models import Project, ProjectMembership

# Get your user
username = 'nikhildhankhad'  # Change this to your actual username
try:
    user = User.objects.get(username=username)
    print(f"✓ Found user: {user.username}")
    
    # Get all projects
    all_projects = Project.objects.all()
    print(f"\n📊 Total projects: {all_projects.count()}")
    
    for project in all_projects:
        print(f"\n📁 Project: {project.name}")
        print(f"   Current owner: {project.owner.username}")
        
        # Make you the owner
        project.owner = user
        project.save()
        print(f"   ✓ Changed owner to: {user.username}")
        
        # Ensure you have owner membership
        membership, created = ProjectMembership.objects.get_or_create(
            project=project,
            user=user,
            defaults={'role': 'owner'}
        )
        if not created and membership.role != 'owner':
            membership.role = 'owner'
            membership.save()
            print(f"   ✓ Updated membership role to: owner")
        elif created:
            print(f"   ✓ Created owner membership")
        else:
            print(f"   ✓ Already owner member")
    
    print(f"\n✅ SUCCESS! You are now the owner of all {all_projects.count()} projects!")
    print(f"🎉 Refresh your browser to see Edit, Delete, and Mark as Complete buttons!")
    
except User.DoesNotExist:
    print(f"❌ ERROR: User '{username}' not found!")
    print("Available users:")
    for u in User.objects.all():
        print(f"  - {u.username}")
