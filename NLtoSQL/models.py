from django.db import models
from django.contrib.auth.models import User
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
