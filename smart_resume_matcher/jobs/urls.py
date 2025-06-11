from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('', views.job_list_view, name='job_list'),
    path('search/', views.job_search_view, name='job_search'),
    path('ai-matches/', views.ai_job_matches_view, name='ai_job_matches'),
    path('detail/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('application/<int:job_id>/', views.job_application_view, name='job_application'),
    
    # API endpoints
    path('api/job-description/<int:job_id>/', api.get_formatted_job_description, name='api_job_description'),
]
