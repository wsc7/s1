from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ReminderSetting
from .views import create_user_reminder_settings


@receiver(post_save, sender=User)
def create_user_reminder_settings_signal(sender, instance, created, **kwargs):
    """当创建新用户时，自动创建提醒设置"""
    if created:
        create_user_reminder_settings(instance)