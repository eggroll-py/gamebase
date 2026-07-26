from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    bio = models.TextField(blank=True, default='')
    avatar_url = models.URLField(blank=True, default='')
    favourite_platform = models.TextField(blank=True, null=True)