# Django Project Collaboration Portal (Collab Apps)

A complete web-based collaboration platform where teams can create projects, manage tasks, share files, and communicate with role-based permissions and real-time notifications.

## Features

### ✨ Core Features

- **User Authentication**
  - User registration with field-specific error messages
  - Login/logout with clear error feedback
  - Password validation and security

- **Project Management**
  - Create, edit, and delete projects
  - Project status tracking (Active/Archived)
  - Rich project descriptions
  - Activity feed for project events

- **Role-Based Permissions** (using django-guardian)
  - **Owner**: Full control of project, manage members and settings
  - **Editor**: Create/edit tasks, comments, and files
  - **Viewer**: Read-only access to project content

- **Task Management**
  - Create, edit, and delete tasks
  - Task status tracking (To Do, In Progress, Done)
  - Priority levels (Low, Medium, High)
  - Due dates
  - Assign up to 5 members per task (configurable)
  - Task filtering by status

- **Comments & @Mentions**
  - Comment on projects and tasks
  - @mention team members to notify them
  - Automatic notification creation for mentions
  - Only project members can be mentioned

- **File Uploads**
  - Upload files to projects or tasks
  - Supported formats: PDF, DOC, DOCX, XLS, XLSX, PNG, JPG, JPEG
  - Maximum file size: 5MB (configurable)
  - Secure file downloads with permission checks

- **Notification System**
  - Real-time notification badge in navbar
  - Notifications for:
    - @mentions in comments
    - Task assignments
    - Being added to a project
  - Mark notifications as read
  - Notification panel and full page view

- **Activity Feed**
  - Track all project activities
  - See who did what and when
  - Activity types: project created, task created, comment added, file uploaded, member added

## Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (development) - easily switchable to PostgreSQL
- **Permissions**: django-guardian for object-level permissions
- **Frontend**: Bootstrap 5 with modern gradient design
- **Icons**: Bootstrap Icons

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Step 1: Clone or Download the Project

```bash
cd "PROJ PORTAL"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- Django>=4.2,<5.0
- django-guardian>=2.4.0
- Pillow>=10.0.0

### Step 5: Run Migrations

```bash
python manage.py migrate
```

This will create all necessary database tables for:
- Projects, Tasks, Comments, Files
- Notifications, Activity Feed
- ProjectMembership (roles)
- Guardian permissions

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 7: Run Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser.

## Configuration

### Django-Guardian Setup

The project is already configured with django-guardian. The settings include:

```python
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Default
    'guardian.backends.ObjectPermissionBackend',  # Guardian
)
```

### Media and Static Files

**Media Files** (user uploads):
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Static Files** (CSS, JS, images):
```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

In production, collect static files:
```bash
python manage.py collectstatic
```

### Custom Settings

You can adjust these in `collab_portal/settings.py`:

```python
MAX_TASK_ASSIGNEES = 5  # Maximum assignees per task
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
ALLOWED_FILE_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg']
```

## How It Works

### Notification System

Notifications are automatically created when:

1. **@Mentions**: When a user mentions another user in a comment using `@username`
   - The mentioned user must be a project member
   - No notification for self-mentions
   - Regex pattern: `r'@(\w+)'`

2. **Task Assignment**: When a user is assigned to a task
   - Notification created via Django signals
   - Only for new assignments

3. **Member Added**: When a user is added to a project
   - Notification shows the role they were assigned

The notification badge in the navbar updates automatically every 30 seconds via AJAX.

### @Mention System

When you type a comment:
1. Use `@username` to mention someone
2. On submit, the comment is parsed for @mentions
3. For each mentioned user:
   - Check if they're a project member
   - Create a notification if valid
   - Avoid duplicates

### Permission Enforcement

Permissions are checked at multiple levels:

1. **View Mixins**: `ProjectMemberRequiredMixin`, `ProjectEditorRequiredMixin`, `ProjectOwnerRequiredMixin`
2. **Helper Functions**: `is_project_owner()`, `has_project_edit_access()`, `has_project_view_access()`
3. **Template Logic**: Buttons and forms only shown to authorized users

### File Upload Security

Files are validated for:
- **Extension**: Only allowed file types can be uploaded
- **Size**: Maximum 5MB enforced server-side
- **Permissions**: Only project members can download files

## Running Tests

The project includes comprehensive tests covering:

- Project creation with members and roles
- Task assignment with max assignees limit
- Comment linking validation
- File upload validation (type and size)
- Permission enforcement
- @mention behavior and notification creation
- Authentication error messages
- Notification marking as read

Run all tests:
```bash
python manage.py test
```

Run specific test class:
```bash
python manage.py test projects.tests.ProjectModelTest
```

## Project Structure

```
PROJ PORTAL/
├── collab_portal/          # Main project settings
│   ├── settings.py         # Configuration
│   ├── urls.py             # Root URL routing
│   └── wsgi.py
├── accounts/               # Authentication app
│   ├── forms.py            # Custom auth forms
│   ├── views.py            # Login, register, logout
│   └── urls.py
├── projects/               # Core collaboration app
│   ├── models.py           # All models
│   ├── views.py            # All views
│   ├── forms.py            # All forms
│   ├── permissions.py      # Permission helpers
│   ├── validators.py       # File validators
│   ├── signals.py          # Auto-create notifications
│   ├── admin.py            # Admin configuration
│   ├── tests.py            # Comprehensive tests
│   └── urls.py
├── core/                   # Shared utilities
│   └── mixins.py           # Permission mixins
├── templates/              # All HTML templates
│   ├── base.html           # Base template with navbar
│   ├── accounts/           # Auth templates
│   └── projects/           # Project templates
├── media/                  # User uploads (created automatically)
├── manage.py
└── requirements.txt
```

## Usage Guide

### Creating Your First Project

1. Register an account or log in
2. Click "Create Project" in the navbar
3. Fill in project name and description
4. You're automatically added as the Owner

### Adding Team Members

1. Go to your project
2. Click "Manage Members"
3. Select a user and assign a role (Editor or Viewer)
4. They'll receive a notification

### Creating Tasks

1. Open a project
2. Go to the "Tasks" tab
3. Click "New Task"
4. Fill in details and assign team members (up to 5)
5. Assignees receive notifications

### Using @Mentions

In any comment box, type `@username` to mention someone:
```
@alice can you review this?
@bob please update the design
```

They'll receive a notification with a link to the comment.

### Uploading Files

1. Go to the "Files" tab in a project or task
2. Click "Upload File"
3. Select a file (max 5MB, allowed types only)
4. File is available to all project members

## Admin Panel

Access the Django admin at http://127.0.0.1:8000/admin/

You can manage:
- Users
- Projects and Memberships
- Tasks and Assignees
- Comments
- Files
- Notifications
- Activity Feed

## Production Deployment

For production deployment:

1. **Set DEBUG = False** in settings.py
2. **Configure ALLOWED_HOSTS**
3. **Use PostgreSQL** instead of SQLite
4. **Set up proper SECRET_KEY**
5. **Configure static file serving** (use WhiteNoise or CDN)
6. **Set up media file storage** (use S3 or similar)
7. **Enable HTTPS**
8. **Set up email backend** for notifications (optional)

## Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic
```

### Migrations not applying
```bash
python manage.py makemigrations
python manage.py migrate
```

### Permission denied errors
Make sure you're logged in and are a member of the project.

### File upload fails
Check file size (<5MB) and extension (PDF, DOC, DOCX, XLS, XLSX, PNG, JPG, JPEG).

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please check the code comments or create an issue in the repository.

---

**Built with Django 4.2 and Bootstrap 5** 🚀
