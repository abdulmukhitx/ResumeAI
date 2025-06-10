from django.contrib import admin
from .models import Job, JobMatch, JobSearch, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'location', 'salary_range', 'published_at', 'is_active')
    list_filter = ('employment_type', 'location', 'published_at', 'is_active')
    search_fields = ('title', 'company_name', 'hh_id')
    readonly_fields = ('hh_id', 'hh_url', 'published_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('hh_id', 'title', 'company_name', 'company_url', 'hh_url')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'responsibilities')
        }),
        ('Employment', {
            'fields': ('location', 'salary_from', 'salary_to', 'salary_currency', 
                      'employment_type', 'experience_required')
        }),
        ('Skills', {
            'fields': ('required_skills', 'optional_skills'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('published_at', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'match_score', 'created_at')
    list_filter = ('match_score', 'created_at')
    search_fields = ('user__email', 'job__title', 'job__company_name')
    readonly_fields = ('match_score', 'matching_skills', 'missing_skills')
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job Title'

@admin.register(JobSearch)
class JobSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'search_query', 'matches_found', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'search_query')
    readonly_fields = ('started_at', 'completed_at', 'total_found', 'jobs_analyzed', 'matches_found')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'status', 'applied_date', 'last_status_update')
    list_filter = ('status', 'applied_date', 'last_status_update')
    search_fields = ('user__email', 'job__title', 'job__company_name')
    readonly_fields = ('applied_date',)
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job Title'