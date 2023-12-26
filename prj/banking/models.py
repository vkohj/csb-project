from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group
from datetime import datetime, timedelta
from django.utils import timezone

# Create your models here.
class Account(models.Model):
    num = models.TextField(max_length=12, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.IntegerField()

class Log(models.Model):
    hidden = models.BooleanField()
    type = models.TextField()
    name = models.TextField(blank=True, null=True)
    acc1 = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="user1", blank=True, null=True)
    acc2 = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="user2", blank=True, null=True)
    
    sdetail1 = models.TextField(blank=True, null=True)
    sdetail2 = models.TextField(blank=True, null=True)
    ldetail = models.TextField(blank=True, null=True)

    ip = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

class Admin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class LoginAttempts(models.Model):
    username = models.TextField()
    ip = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def pastExpiry(self):
        return (timezone.now() - self.date) > timedelta(minutes=3)

