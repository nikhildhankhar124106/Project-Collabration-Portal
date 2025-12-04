import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collab_portal.settings')
django.setup()

from projects.models import Task

# Find and delete the k4p task
try:
    k4p_tasks = Task.objects.filter(title__icontains='k4p')
    
    if k4p_tasks.exists():
        print(f"Found {k4p_tasks.count()} task(s) matching 'k4p':")
        for task in k4p_tasks:
            print(f"  - ID: {task.id}, Title: {task.title}, Project: {task.project.name}")
            task.delete()
            print(f"  ✓ Deleted task: {task.title}")
        print(f"\n✅ Successfully deleted all k4p tasks!")
    else:
        print("❌ No tasks found with 'k4p' in the title")
        print("\nAll tasks:")
        for task in Task.objects.all():
            print(f"  - {task.title} (ID: {task.id})")
            
except Exception as e:
    print(f"❌ Error: {e}")
