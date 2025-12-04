---
description: Deploy the Django Collaboration Portal to production
---

# Deployment Workflow

This workflow guides you through deploying the Django Project Collaboration Portal.

## Choose Your Platform

1. **Render** (Recommended) - Modern platform, free tier available, easy setup
2. **Railway** - Good alternative, free tier available
3. **Heroku** - Traditional choice, $5+/month
4. **PythonAnywhere** - Django-specific, free tier available
5. **DigitalOcean/AWS** - Advanced, full control


## Quick Start with Render (Recommended)

### 1. Ensure code is in Git repository
```bash
cd "c:\Users\nikhi\Desktop\PROJ PORTAL"
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Deploy using Blueprint
- Go to https://dashboard.render.com/
- Click "New +" → "Blueprint"
- Connect your Git repository
- Select your project repository
- Render will detect `render.yaml` automatically
- Set `ALLOWED_HOSTS` to your Render URL (e.g., `your-app-name.onrender.com`)
- Click "Apply" to deploy

### 3. Monitor deployment
Watch the build logs. Deployment takes 5-10 minutes.

### 4. Create superuser
After deployment succeeds:
- Go to your web service in Render Dashboard
- Click "Shell" tab
- Run: `python manage.py createsuperuser`

### 5. Verify deployment
Visit: `https://your-app-name.onrender.com`

**For detailed instructions, see the comprehensive deployment guide in artifacts.**


## Quick Start with Railway (Easiest)

### 1. Install dependencies
```bash
cd "c:\Users\nikhi\Desktop\PROJ PORTAL"
pip install -r requirements.txt
```

### 2. Initialize Git repository
// turbo
```bash
git init
```

### 3. Add all files to Git
// turbo
```bash
git add .
```

### 4. Commit files
```bash
git commit -m "Initial commit - ready for deployment"
```

### 5. Create GitHub repository
- Go to https://github.com/new
- Create a new repository (don't initialize with README)
- Copy the repository URL

### 6. Add remote and push
```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

### 7. Deploy on Railway
- Go to https://railway.app
- Sign up/login with GitHub
- Click "New Project" → "Deploy from GitHub repo"
- Select your repository
- Railway will auto-detect Django and deploy

### 8. Add PostgreSQL database
- In Railway dashboard, click "New" → "Database" → "PostgreSQL"
- Railway will automatically set DATABASE_URL

### 9. Set environment variables in Railway
Go to your project → Variables tab and add:
```
DJANGO_SETTINGS_MODULE=collab_portal.production_settings
SECRET_KEY=<generate-random-50-char-string>
DEBUG=False
ALLOWED_HOSTS=<your-app-name>.railway.app
```

### 10. Generate SECRET_KEY
Run this locally to generate a secure secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 11. Access your deployed app
- Railway will provide a URL like: https://<your-app-name>.railway.app
- Visit it in your browser

### 12. Create superuser (via Railway terminal)
In Railway dashboard → your service → Terminal:
```bash
python manage.py createsuperuser
```

## Alternative: Deploy to Heroku

### 1. Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

### 2. Login to Heroku
```bash
heroku login
```

### 3. Create Heroku app
```bash
heroku create your-app-name
```

### 4. Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:mini
```

### 5. Set environment variables
```bash
heroku config:set DJANGO_SETTINGS_MODULE=collab_portal.production_settings
heroku config:set SECRET_KEY="<your-secret-key>"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
```

### 6. Deploy
```bash
git push heroku main
```

### 7. Run migrations
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### 8. Open app
```bash
heroku open
```

## Troubleshooting

### Static files not loading
The Procfile includes `collectstatic` in the release command, but you can run manually:
```bash
python manage.py collectstatic --noinput
```

### Database errors
Check that DATABASE_URL is set correctly in environment variables.

### 500 errors
Check logs:
- Railway: View in dashboard → Deployments → Logs
- Heroku: `heroku logs --tail`

### Missing dependencies
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

## Post-Deployment Checklist

- [ ] App is accessible via URL
- [ ] Can login/register users
- [ ] Can create projects
- [ ] Can upload files
- [ ] Static files loading correctly
- [ ] Database working
- [ ] Superuser created
- [ ] SSL/HTTPS enabled

## Important Notes

- Never commit `.env` file (it's in `.gitignore`)
- Keep `SECRET_KEY` secure
- Always use `DEBUG=False` in production
- Set up regular database backups
- Monitor application logs

## Need Help?

See the full deployment guide: `deployment_guide.md`
