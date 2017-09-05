from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.signals import request_finished
from django.contrib.auth.models import User

from .models import Profile


@receiver(post_save, sender=User)
def create_profile_receiver(sender, **kwargs):
    if kwargs['created']:
        Profile.objects.create(user=kwargs['instance'])
