import re

# Read the file
with open(r'c:\Users\nikhi\Desktop\PROJ PORTAL\templates\projects\project_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match the entire conditional block (from {% if task.user_can_access %} to {% endif %})
# We'll replace it with just the link part
pattern = r'(\s+){% if task\.user_can_access %}\s+<a href="{% url \'task_detail\' project\.pk task\.pk %}"\s+class="flex-grow-1 text-decoration-none text-dark">\s+<h6 class="mb-1">{{ task\.title }}</h6>\s+<p class="mb-1 text-muted small">{{ task\.description\|truncatewords:15 }}</p>\s+<div class="mt-2">\s+<span class="badge {{ task\.get_status_badge_class }}">{{ task\.get_status_display }}</span>\s+<span class="badge {{ task\.get_priority_badge_class }}">{{.*?task\.get_priority_display.*?}}</span>\s+{% if task\.due_date %}\s+<span class="badge bg-secondary"><i class="bi bi-calendar"></i> {{ task\.due_date }}</span>\s+{% endif %}\s+</div>\s+</a>\s+{% else %}.*?{% endif %}'

replacement = r'''\1<a href="{% url 'task_detail' project.pk task.pk %}"
\1    class="flex-grow-1 text-decoration-none text-dark">
\1    <h6 class="mb-1">{{ task.title }}</h6>
\1    <p class="mb-1 text-muted small">{{ task.description|truncatewords:15 }}</p>
\1    <div class="mt-2">
\1        <span class="badge {{ task.get_status_badge_class }}">{{ task.get_status_display }}</span>
\1        <span class="badge {{ task.get_priority_badge_class }}">{{ task.get_priority_display }}</span>
\1        {% if task.due_date %}
\1        <span class="badge bg-secondary"><i class="bi bi-calendar"></i> {{ task.due_date }}</span>
\1        {% endif %}
\1    </div>
\1</a>'''

# Apply the replacement
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open(r'c:\Users\nikhi\Desktop\PROJ PORTAL\templates\projects\project_detail.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("File updated successfully!")
