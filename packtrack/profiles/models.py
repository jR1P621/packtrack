from hashlib import sha256
from PIL import Image
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .settings import MAX_AVATAR_RATIO, MAX_AVATAR_SIZE

import datetime


def avatar_upload(instance, filename):
    '''
    Saves profile picture filename as a SHA256 hex digest.
    '''
    return f'profile_avatars/{sha256((filename+datetime.datetime.now().ctime()).encode()).hexdigest()}.png'


class Profile(models.Model):
    '''
    Model for user profile.
    '''
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')
    avatar = models.ImageField(null=True, blank=True, upload_to=avatar_upload)
    hash_name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Rescale avatar to max and crop if user uploads ridiculous dims
        new_avatar = self.avatar
        if new_avatar:
            image = Image.open(self.avatar)
            width, height = image.size
            if width / height > MAX_AVATAR_RATIO:
                width_offset = (width - (height * MAX_AVATAR_RATIO)) // 2
                image.crop(box=(width_offset, 0, width - width_offset, height))
            elif height / width > MAX_AVATAR_RATIO:
                height_offset = (height - (width * MAX_AVATAR_RATIO)) // 2
                image.crop(box=(height_offset, 0, height - height_offset,
                                width))
            factor = 1.0
            if MAX_AVATAR_SIZE < height > width:
                factor = MAX_AVATAR_SIZE / height
            elif MAX_AVATAR_SIZE < width > height:
                factor = MAX_AVATAR_SIZE / width
            size = (int(width * factor), int(height * factor))
            image = image.resize(size, Image.ANTIALIAS)
            image.save(self.avatar.path)

    def get_absolute_url(self):
        return reverse('profile', args=[self.user.username])


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs) -> None:
    '''
    Creates an associated Member instance when a new User is created.
    '''
    if created:
        Profile.objects.create(
            user=instance,
            hash_name=instance.username,
        )
