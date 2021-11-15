from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    followers = models.ManyToManyField(User, blank=True, related_name='followers')
    followed = models.ManyToManyField(User, blank=True, related_name='followed')


class FollowRequest(models.Model):
    STATUS_OPTIONS = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
    ]
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    status = models.CharField(max_length=8, choices=STATUS_OPTIONS, default='pending')


class Idea(models.Model):
    VISIBILITY_OPTIONS = [
        ('public', 'public'),
        ('protected', 'protected'),
        ('private', 'private'),
    ]
    text = models.TextField(max_length=150)
    visibility = models.CharField(max_length=9, choices=VISIBILITY_OPTIONS, default='public')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='idea')
    created_date = models.DateTimeField(default=timezone.now)
