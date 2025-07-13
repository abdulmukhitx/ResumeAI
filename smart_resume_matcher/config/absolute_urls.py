# ABSOLUTE MINIMAL URLs - guaranteed to work
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>✅ Railway Success!</h1><p>Django is working!</p><p><a href='/admin/'>Admin</a></p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]
