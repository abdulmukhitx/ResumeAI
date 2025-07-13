# Minimal URLs - NO DRF, NO JWT, NO problematic imports
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("""
    <h1>Smart Resume Matcher - Railway Deployment</h1>
    <p>✅ Django is running successfully!</p>
    <p><a href="/admin/">Admin Panel</a></p>
    <p>This is a minimal deployment without JWT/DRF to test Railway compatibility.</p>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
