from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.conf import settings
from .models import Teacher

@receiver(pre_delete, sender=Teacher)
def delete_teacher_profile_picture(sender, instance, **kwargs):
    """
    Deletes the profile picture file of a teacher before deleting the teacher object.
    """
    if instance.profile_picture:
        instance.profile_picture.delete() 