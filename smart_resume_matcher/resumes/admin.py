from django.contrib import admin
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'original_filename', 'status', 'created_at', 'is_active')
    list_filter = ('status', 'created_at', 'is_active')
    search_fields = ('user__email', 'original_filename')
    readonly_fields = ('file_size', 'raw_text', 'analysis_started_at', 'analysis_completed_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'file', 'original_filename', 'file_size', 'is_active')
        }),
        ('Analysis Status', {
            'fields': ('status', 'analysis_started_at', 'analysis_completed_at')
        }),
        ('Extracted Content', {
            'fields': ('raw_text',),
            'classes': ('collapse',)
        }),
        ('AI Analysis Results', {
            'fields': ('extracted_skills', 'experience_level', 'job_titles', 'education', 
                      'work_experience', 'analysis_summary', 'confidence_score'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # The `request` argument is intentionally unused
        if obj:  # Editing existing object
            return self.readonly_fields + ('file', 'user')
        return self.readonly_fields