from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list_view, name='job_list'),
    path('search/', views.job_search_view, name='job_search'),
    path('detail/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('application/<int:job_id>/', views.job_application_view, name='job_application'),
]
