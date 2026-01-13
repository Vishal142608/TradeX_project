# TradeX Deployment Guide for Render.com

This guide will walk you through deploying your TradeX Django application to Render.com.

## Prerequisites

Before you begin, ensure you have:

- ✅ A [Render.com](https://render.com) account (free tier available)
- ✅ A [GitHub](https://github.com) account
- ✅ Git installed on your local machine
- ✅ Your TradeX project repository: https://github.com/Vishal142608/TradeX_project

## Step 1: Prepare Your GitHub Repository

### 1.1 Commit All Changes

Make sure all the new deployment files are committed to your repository:

```bash
cd c:\Users\A\OneDrive\Documents\Desktop\TradeX\config_pro
git add .
git commit -m "Add Render.com deployment configuration"
git push origin main
```

**Files that should be in your repository:**
- ✅ `requirements.txt` (updated with production dependencies)
- ✅ `build.sh` (build script for Render)
- ✅ `render.yaml` (Render service configuration)
- ✅ `.env.example` (environment variables template)
- ✅ `config_pro/settings.py` (updated with production settings)
- ✅ `.gitignore` (updated to exclude sensitive files)

### 1.2 Verify .gitignore

Ensure your `.env` file (if it exists) and other sensitive files are NOT pushed to GitHub:

```bash
git status
```

Make sure `.env`, `__pycache__/`, and `staticfiles/` are not listed.

## Step 2: Create PostgreSQL Database on Render

### 2.1 Log in to Render.com

1. Go to [https://render.com](https://render.com)
2. Click **Sign In** or **Get Started**
3. Sign in with your GitHub account (recommended for easy integration)

### 2.2 Create a New PostgreSQL Database

1. From the Render Dashboard, click **New +** button
2. Select **PostgreSQL**
3. Configure the database:
   - **Name**: `tradex-db`
   - **Database**: `tradex`
   - **User**: `tradex` (auto-generated)
   - **Region**: Choose the closest region to you
   - **PostgreSQL Version**: 16 (or latest)
   - **Plan**: Free (or choose a paid plan for better performance)
4. Click **Create Database**

### 2.3 Save Database Credentials

Once created, you'll see the database details page. **Important:** Copy the **Internal Database URL** - you'll need this later.

It will look like:
```
postgresql://tradex:password@dpg-xxxxx-a.oregon-postgres.render.com/tradex_xxxx
```

## Step 3: Create Web Service on Render

### 3.1 Create New Web Service

1. From the Render Dashboard, click **New +** button
2. Select **Web Service**
3. Connect your GitHub repository:
   - If this is your first time, click **Connect GitHub**
   - Authorize Render to access your repositories
   - Search for `TradeX_project`
   - Click **Connect**

### 3.2 Configure Web Service

Fill in the following details:

**Basic Settings:**
- **Name**: `tradex` (or your preferred name)
- **Region**: Same region as your database
- **Branch**: `main` (or your default branch)
- **Root Directory**: `config_pro`
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn config_pro.wsgi:application`

**Instance Type:**
- Select **Free** (or choose a paid plan)

### 3.3 Configure Environment Variables

Scroll down to **Environment Variables** section and add the following:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `SECRET_KEY` | Generate a new secret key (see below) |
| `DEBUG` | `False` |
| `DATABASE_URL` | Paste the Internal Database URL from Step 2.3 |

**To generate a SECRET_KEY:**

Run this command on your local machine:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it as the `SECRET_KEY` value.

**Important:** Render will automatically set `RENDER_EXTERNAL_HOSTNAME` - you don't need to add it manually.

### 3.4 Deploy

1. Click **Create Web Service**
2. Render will start building and deploying your application
3. Monitor the deployment logs in real-time

**Expected build process:**
- Installing dependencies from `requirements.txt`
- Running database migrations
- Collecting static files
- Starting the Gunicorn server

## Step 4: Verify Deployment

### 4.1 Check Build Logs

Watch the logs for any errors. A successful deployment will show:

```
==> Running migrations...
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, main, sessions
Running migrations:
  ...

==> Collecting static files...
X static files copied to '/opt/render/project/src/config_pro/staticfiles'

==> Starting server...
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:10000
```

### 4.2 Access Your Live Site

Once deployment is complete, Render will provide you with a URL like:

```
https://tradex-xxxx.onrender.com
```

Click on the URL to open your deployed application.

### 4.3 Test Core Functionality

Test the following features on your live site:

1. **Home Page**
   - [ ] Home page loads correctly
   - [ ] Tailwind CSS styles are applied
   - [ ] Navigation works

2. **User Authentication**
   - [ ] Register a new account
   - [ ] Log in with the new account
   - [ ] Log out

3. **Dashboard**
   - [ ] Dashboard displays correctly
   - [ ] Market overview shows stock data
   - [ ] Charts render properly

4. **Trading Features**
   - [ ] Buy stocks
   - [ ] View portfolio
   - [ ] Sell stocks
   - [ ] View transaction history

5. **Additional Features**
   - [ ] Watchlist functionality
   - [ ] SIP page loads
   - [ ] F&O page loads
   - [ ] Profile page displays user info

## Step 5: Post-Deployment Configuration

### 5.1 Create Superuser (Optional)

To access the Django admin panel, you'll need to create a superuser.

1. Go to your Render Dashboard
2. Navigate to your `tradex` web service
3. Click on the **Shell** tab
4. Run the following command:

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 5.2 Access Django Admin

Visit `https://your-app-url.onrender.com/admin` and log in with your superuser credentials.

## Troubleshooting

### Issue: Build Fails with "Permission Denied" for build.sh

**Solution:** Make the build script executable before pushing to GitHub:

```bash
cd c:\Users\A\OneDrive\Documents\Desktop\TradeX\config_pro
git update-index --chmod=+x build.sh
git commit -m "Make build.sh executable"
git push origin main
```

Then trigger a manual redeploy on Render.

### Issue: Static Files Not Loading

**Symptoms:** CSS styles missing, images not displaying

**Solution:**
1. Check that `STATIC_ROOT` is set in `settings.py`
2. Verify WhiteNoise is in `MIDDLEWARE`
3. Check build logs to ensure `collectstatic` ran successfully
4. Clear browser cache and hard reload (Ctrl+Shift+R)

### Issue: Database Connection Error

**Symptoms:** "OperationalError: could not connect to server"

**Solution:**
1. Verify `DATABASE_URL` environment variable is set correctly
2. Ensure you're using the **Internal Database URL** from Render
3. Check that the database is in the same region as your web service
4. Verify the database is running (check Render dashboard)

### Issue: CSRF Verification Failed

**Symptoms:** "CSRF verification failed" error when submitting forms

**Solution:**
1. Ensure `CSRF_TRUSTED_ORIGINS` includes your Render domain
2. Verify `SECURE_PROXY_SSL_HEADER` is set in production settings
3. Check that `RENDER_EXTERNAL_HOSTNAME` is automatically set by Render

### Issue: Application Crashes on Startup

**Solution:**
1. Check the deployment logs for error messages
2. Verify all environment variables are set correctly
3. Ensure `requirements.txt` includes all dependencies
4. Check that migrations ran successfully

### Issue: Free Tier Limitations

**Note:** Render's free tier has some limitations:
- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- 750 hours/month of runtime
- Limited database storage (1GB)

**Solution:** Consider upgrading to a paid plan for production use.

## Updating Your Deployment

When you make changes to your code:

1. **Commit and push changes to GitHub:**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **Automatic Deployment:**
   - Render will automatically detect the changes and redeploy
   - Monitor the deployment in the Render dashboard

3. **Manual Deployment:**
   - Go to your web service in Render dashboard
   - Click **Manual Deploy** → **Deploy latest commit**

## Environment Variables Reference

Here's a complete list of environment variables used:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | `django-insecure-xyz123...` |
| `DEBUG` | Debug mode (always False in production) | `False` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `PYTHON_VERSION` | Python version to use | `3.11.0` |
| `RENDER_EXTERNAL_HOSTNAME` | Auto-set by Render | `tradex-xxxx.onrender.com` |

## Security Checklist

Before going live, ensure:

- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` is unique and not in source code
- [ ] Database credentials are not in source code
- [ ] `.env` file is in `.gitignore`
- [ ] `ALLOWED_HOSTS` is properly configured
- [ ] `CSRF_TRUSTED_ORIGINS` includes your domain
- [ ] HTTPS is enabled (automatic on Render)

## Performance Optimization

For better performance:

1. **Enable Caching:** Consider using Redis for caching (requires paid plan)
2. **Database Indexing:** Add indexes to frequently queried fields
3. **CDN for Static Files:** Use a CDN for static assets (optional)
4. **Upgrade Plan:** Consider upgrading from free tier for production

## Support and Resources

- **Render Documentation:** https://render.com/docs
- **Django Deployment Checklist:** https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- **Render Community:** https://community.render.com/

## Next Steps

After successful deployment:

1. **Custom Domain (Optional):**
   - Go to your web service settings
   - Add a custom domain
   - Update DNS records as instructed

2. **Monitoring:**
   - Set up monitoring and alerts in Render dashboard
   - Monitor application logs regularly

3. **Backups:**
   - Configure database backups (available on paid plans)
   - Export data regularly

4. **SSL Certificate:**
   - Render provides free SSL certificates automatically
   - Verify HTTPS is working

---

## Quick Reference: Deployment Commands

```bash
# 1. Commit changes
git add .
git commit -m "Deployment configuration"
git push origin main

# 2. Generate SECRET_KEY (run locally)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 3. Make build.sh executable (if needed)
git update-index --chmod=+x build.sh
git commit -m "Make build.sh executable"
git push origin main

# 4. Create superuser (run in Render Shell)
python manage.py createsuperuser
```

---

**Congratulations! Your TradeX application is now live on Render.com! 🎉**

Share your live URL: `https://your-app-name.onrender.com`
