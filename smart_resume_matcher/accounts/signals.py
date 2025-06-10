# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .models import User

@receiver(post_save, sender=User)
def create_user_profile(_sender, instance, created, **_kwargs):
    if created:
        UserProfile = apps.get_model('accounts', 'UserProfile')  # Dynamically load the UserProfile model
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(_sender, instance, **_kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()