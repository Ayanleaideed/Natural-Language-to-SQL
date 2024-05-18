from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # profile_picture = models.ImageField(upload_to='profile_pics', null=True, blank=True)

    def __str__(self):
        return self.user.username

def get_upload_path(instance, filename):
    return os.path.join('databases', filename)

class DatabaseType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class DatabaseUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=get_upload_path)
    size = models.PositiveIntegerField(blank=True, null=True, editable=False)
    type = models.ForeignKey(DatabaseType, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.size = self.file.size
        super(DatabaseUpload, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} uploaded by {self.user.username}'




# This Model will help keep  track the users requests to prevent spamming 
class APIUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def check_rate_limit(cls, user, endpoint, max_requests, period):
        now = timezone.now()
        period_ago = now - timezone.timedelta(seconds=period)
        requests = cls.objects.filter(user=user, endpoint=endpoint, timestamp__gte=period_ago)
        count = requests.count()
        
        if count < max_requests:
            return True, 0
        
        oldest_request = requests.earliest('timestamp')
        wait_time = (oldest_request.timestamp + timezone.timedelta(seconds=period) - now).total_seconds()
        return False, wait_time

    @classmethod
    def get_users_again(cls):
        return cls.objects.values_list('user', flat=True).distinct()
    
    
class is_allowed_SQL_beta(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Is_allowed = models.BooleanField(blank=False, null=False)