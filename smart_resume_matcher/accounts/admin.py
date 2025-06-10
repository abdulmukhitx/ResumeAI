from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.apps import apps

# Dynamically load UserProfile model to avoid potential circular import issues
UserProfile = apps.get_model('accounts', 'UserProfile')

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone', 'location')
        }),
        ('Job Preferences', {
            'fields': ('desired_position', 'experience_level', 'employment_types', 'preferred_locations')
        }),
        ('Salary Preferences', {
            'fields': ('min_salary', 'max_salary', 'salary_currency')
        }),
        ('Job Search Settings', {
            'fields': ('is_job_search_active', 'weekly_job_emails', 'last_job_search')
        }),
        ('Skills', {
            'fields': ('skills',)
        }),
    )

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('is_email_verified',)
        }),
    )
    
    inlines = [UserProfileInline]

# Register UserProfile in the admin site for better visibility
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'location', 'is_job_search_active')
    search_fields = ('user__email', 'first_name', 'last_name', 'location')
    list_filter = ('is_job_search_active', 'weekly_job_emails')

