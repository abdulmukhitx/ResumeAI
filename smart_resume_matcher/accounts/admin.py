from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile

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

# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()