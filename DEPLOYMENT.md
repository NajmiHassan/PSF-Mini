# Deployment Guide for Mini-PSF

This guide covers three free options for deploying your Django site so you can share a live link with your professor.

---

## Option 1: PythonAnywhere (Easiest — recommended for beginners)

**Pros:** Truly free forever, no credit card, doesn't sleep, made specifically for Python.
**Cons:** Free tier gives you `yourname.pythonanywhere.com` (cannot use custom domain).

### Step-by-step

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com/) — choose the **"Beginner"** (free) plan.

2. **Push your code to GitHub first** (so you can clone it on PythonAnywhere):
   ```bash
   # In your Codespace terminal:
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Open a Bash console** on PythonAnywhere (top right → "Consoles" → "Bash").

4. **Clone your repo:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/PSF-Mini.git
   cd PSF-Mini
   ```

5. **Create a virtual environment and install packages:**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 psf-env
   pip install -r requirements.txt
   ```

6. **Run migrations and collect static files:**
   ```bash
   python manage.py makemigrations scaffold_filler
   python manage.py migrate
   python manage.py collectstatic --no-input
   ```

7. **Create the web app:**
   - Go to the **Web** tab → **Add a new web app**.
   - Pick **Manual configuration** → **Python 3.10**.

8. **Configure the web app** (on the Web tab):
   - **Source code:** `/home/YOUR_USERNAME/PSF-Mini`
   - **Working directory:** `/home/YOUR_USERNAME/PSF-Mini`
   - **WSGI configuration file:** click the link and replace its contents with:
     ```python
     import os
     import sys

     path = '/home/YOUR_USERNAME/PSF-Mini'
     if path not in sys.path:
         sys.path.insert(0, path)

     os.environ['DJANGO_SETTINGS_MODULE'] = 'scaffold_app.settings'
     os.environ['DJANGO_DEBUG'] = 'False'
     os.environ['DJANGO_ALLOWED_HOSTS'] = 'YOUR_USERNAME.pythonanywhere.com'
     os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = 'https://YOUR_USERNAME.pythonanywhere.com'
     os.environ['DJANGO_SECRET_KEY'] = 'paste-a-long-random-string-here'

     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```
   - **Virtualenv:** `/home/YOUR_USERNAME/.virtualenvs/psf-env`

9. **Set static files mapping** (still on the Web tab, scroll down to "Static files"):
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/PSF-Mini/staticfiles`

10. **Click the big green "Reload" button at the top.**

11. **Visit `https://YOUR_USERNAME.pythonanywhere.com`** — done!

---

## Option 2: Render (Modern, polished)

**Pros:** Modern UI, GitHub auto-deploys, free SSL.
**Cons:** Free instances sleep after 15 min of inactivity (cold start ~30 sec on first hit).

### Step-by-step

1. **Push your code to GitHub** (same as step 2 above).

2. **Sign up** at [render.com](https://render.com) using your GitHub account.

3. **Make `build.sh` executable** (run this in your Codespace before pushing):
   ```bash
   chmod +x build.sh
   git add build.sh
   git commit -m "Make build.sh executable"
   git push
   ```

4. **On Render:** click **"New +"** → **"Web Service"** → connect your GitHub repo.

5. **Configure the service:**
   - **Name:** `psf-mini` (or anything — becomes part of the URL)
   - **Region:** pick one near you
   - **Branch:** `main`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn scaffold_app.wsgi:application`
   - **Instance Type:** `Free`

6. **Add environment variables** (scroll down to "Environment Variables"):
   | Key | Value |
   |---|---|
   | `DJANGO_SECRET_KEY` | (click "Generate" — Render makes one for you) |
   | `DJANGO_DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | `psf-mini.onrender.com` (replace with your actual URL after first deploy) |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://psf-mini.onrender.com` |
   | `PYTHON_VERSION` | `3.11.0` |

7. **Click "Create Web Service"** — Render will build and deploy automatically. Takes 2-3 minutes.

8. **Visit your URL** (shown at the top of the Render dashboard).

> **Tip:** After the first deploy, update `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` with the actual URL Render assigned you. Then click "Manual Deploy → Clear build cache & deploy".

---

## Option 3: Railway (Fast, dev-friendly)

**Pros:** Very fast deploys, doesn't sleep, great UI.
**Cons:** Only $5 free credit — runs out in ~3 weeks of continuous use. Fine for a demo.

### Step-by-step

1. **Push to GitHub.**

2. **Sign up** at [railway.app](https://railway.app) with GitHub.

3. **Click "New Project"** → **"Deploy from GitHub repo"** → pick your repo.

4. **Railway auto-detects Django** and starts deploying. While that runs:

5. **Click your service → Variables tab** → add:
   | Key | Value |
   |---|---|
   | `DJANGO_SECRET_KEY` | a long random string |
   | `DJANGO_DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | (the domain Railway gives you, e.g. `psf-mini-production.up.railway.app`) |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://psf-mini-production.up.railway.app` |

6. **Settings tab → Networking → "Generate Domain"** to get a public URL.

7. **Add a deploy command** (Settings → Deploy → Custom Start Command):
   ```
   python manage.py makemigrations scaffold_filler && python manage.py migrate && python manage.py collectstatic --no-input && gunicorn scaffold_app.wsgi
   ```

8. **Wait ~2 minutes, visit your domain.**

---

## Common troubleshooting

### "DisallowedHost at /"
Your domain isn't in `DJANGO_ALLOWED_HOSTS`. Add it (without `https://`, just the domain).

### "CSRF verification failed" on the form
Add the full domain (WITH `https://`) to `DJANGO_CSRF_TRUSTED_ORIGINS`.

### CSS isn't loading
You forgot `collectstatic`. The `build.sh` script handles this on Render. On PythonAnywhere, run it manually.

### "no such table" error
Migrations weren't run. Run `python manage.py migrate` (and `makemigrations scaffold_filler` first if needed).

### App is super slow on first visit (Render only)
That's the free tier sleeping. First request wakes it up (~30 sec), subsequent requests are fast.

---

## What to send your professor

Once deployed, you can send something like:

> *"Hi Professor, I built a simplified web tool inspired by your work on PSF. The live demo is at: `https://psf-mini.onrender.com` (or whichever URL). Source code: `https://github.com/yourusername/PSF-Mini`. The README and About page explain how it differs from your original system."*
