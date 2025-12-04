import re

# Read the file
with open(r'c:\Users\nikhi\Desktop\PROJ PORTAL\templates\projects\project_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the leftover lines (closing divs and endif)
content = content.replace(
    """                    </a>
                        </div>
                    </div>
                    {% endif %}
                    <div class="d-flex align-items-center ms-3">""",
    """                    </a>
                    <div class="d-flex align-items-center ms-3">"""
)

# Write back
with open(r'c:\Users\nikhi\Desktop\PROJ PORTAL\templates\projects\project_detail.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Template cleaned successfully!")
