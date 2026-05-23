"""URL configuration for the Mini-PSF project."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # All app URLs live in the scaffold_filler app
    path('', include('scaffold_filler.urls')),
]
