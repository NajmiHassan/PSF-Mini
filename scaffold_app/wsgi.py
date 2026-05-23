"""WSGI config for the Mini-PSF project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scaffold_app.settings')
application = get_wsgi_application()
