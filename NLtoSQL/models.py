import os
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import tempfile
import requests
import io
import boto3
from botocore.exceptions import ClientError
from django.conf import settings




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

HOST_CHOICES = [
    ('localhost', 'Local Host'),
    ('cloud', 'Cloud Host'),
    ('os_file', 'OS File Host'),
    ("Self-Hosted", 'Self Hosted'),
    ('other_hosts', 'Other Hosts'),
    ('N/A', 'N/A')
]



def get_b2_client():
    return boto3.client(
        's3',
        endpoint_url=f'https://s3.{settings.B2_REGION}.backblazeb2.com',
        aws_access_key_id=settings.B2_APPLICATION_KEY_ID,
        aws_secret_access_key=settings.B2_APPLICATION_KEY
    )
class DatabaseUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.PositiveIntegerField(blank=True, null=True, editable=False)
    type = models.ForeignKey(DatabaseType, on_delete=models.CASCADE)
    hostType = models.CharField(max_length=255, blank=True, null=True, choices=HOST_CHOICES)
    b2_file_key = models.CharField(max_length=255, default=None, null=True)

    def save(self, *args, **kwargs):
        if not self.b2_file_key:
            raise ValueError("b2_file_key must be set")
        super().save(*args, **kwargs)

    def delete_from_b2(self):
        if self.b2_file_key:
            try:
                b2_client = get_b2_client()
                b2_client.delete_object(Bucket=settings.B2_BUCKET_NAME, Key=self.b2_file_key)
            except ClientError as e:
                return e
        return None

    def delete(self, *args, **kwargs):
        # Delete file from B2 before deleting the database record
        error = self.delete_from_b2()
        if error:
            raise Exception(f"Error deleting file from B2: {str(error)}")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f'{self.name} uploaded by {self.user.username}'

    @property
    def file_path(self):
        return self.b2_file_key

    @property
    def file(self):
        class B2File:
            def __init__(self, upload):
                self.upload = upload

            @property
            def path(self):
                return self.upload.b2_file_key

            @property
            def url(self):
                b2_client = get_b2_client()
                try:
                    return b2_client.generate_presigned_url('get_object',
                                                            Params={'Bucket': settings.B2_BUCKET_NAME,
                                                                    'Key': self.upload.b2_file_key},
                                                            ExpiresIn=3600)
                except ClientError as e:
                    print(e)
                    return None

            def open(self, mode='rb'):
                if mode != 'rb':
                    raise ValueError("Only read mode is supported")
                b2_client = get_b2_client()
                response = b2_client.get_object(Bucket=settings.B2_BUCKET_NAME, Key=self.upload.b2_file_key)
                return io.BytesIO(response['Body'].read())

        return B2File(self)




class DatabaseConnection(models.Model):
    database = models.ForeignKey(DatabaseUpload, on_delete=models.CASCADE)
    host = models.CharField(max_length=255, blank=False, null=False)
    port = models.IntegerField( blank=False, null=False)
    dbname = models.CharField(max_length=255,  blank=False, null=False)
    user = models.CharField(max_length=255,  blank=False, null=False)
    password = models.CharField(max_length=255,  blank=False, null=False)
    connection_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.database.name} connection"

# This Model will help keep  track the users requests to prevent spamming
class APIUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=255)
    user_input_request_context = models.TextField(blank=True, null=True)
    model_response = models.TextField(blank=True, null=True)
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




class QueryHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    database = models.ForeignKey(DatabaseUpload, on_delete=models.CASCADE)
    query_type = models.CharField(max_length=100)
    query_nl_text = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

# models to handle permission  
class DatabasePermissions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_select = models.BooleanField(default=False)
    can_insert = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_drop = models.BooleanField(default=False)


