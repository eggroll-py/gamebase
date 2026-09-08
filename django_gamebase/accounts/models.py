from django.contrib.auth.models import AbstractUser
from django.db import models

class Visibility(models.TextChoices):
    PUBLIC = 'public', 'Public'
    PRIVATE = 'private', 'Private'
    FOLLOWERS = 'followers', 'Followers Only'

class User(AbstractUser):
    bio = models.TextField(blank=True, default='')
    avatar_url = models.URLField(blank=True, default='')
    favourite_platform = models.TextField(blank=True, null=True)
    profile_visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)