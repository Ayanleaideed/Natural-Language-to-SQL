import io
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.cache import cache
import hashlib

def get_b2_client():
    return boto3.client(
        's3',
        endpoint_url=f'https://s3.{settings.B2_REGION}.backblazeb2.com',
        aws_access_key_id=settings.B2_APPLICATION_KEY_ID,
        aws_secret_access_key=settings.B2_APPLICATION_KEY
    )

def get_cache_key(file_key, prefix='b2_file'):
    """Generate a unique cache key for a file."""
    return f"{prefix}_{hashlib.md5(file_key.encode()).hexdigest()}"

def download_from_b2(file_key):
    cache_key = get_cache_key(file_key)
    cached_content = cache.get(cache_key)

    if cached_content:
        return io.BytesIO(cached_content)

    b2_client = get_b2_client()
    try:
        response = b2_client.get_object(Bucket=settings.B2_BUCKET_NAME, Key=file_key)
        file_content = response['Body'].read()
        
        # Cache the file content (adjust timeout as needed)
        cache.set(cache_key, file_content, timeout=3600)  # Cache for 1 hour
        
        return io.BytesIO(file_content)
    except ClientError as e:
        raise Exception(f"Error downloading file from B2: {str(e)}")

def upload_to_b2(file_data, file_key):
    b2_client = get_b2_client()
    try:
        if hasattr(file_data, 'read'):
            file_data = file_data.read()
        
        response = b2_client.put_object(
            Bucket=settings.B2_BUCKET_NAME,
            Key=file_key,
            Body=file_data
        )
        
        # Invalidate the cache for this file key
        cache_key = get_cache_key(file_key)
        cache.delete(cache_key)
        
        return response
    except ClientError as e:
        raise Exception(f"Error uploading file to B2: {str(e)}")

def get_b2_file_url(file_key, expires_in=3600):
    cache_key = get_cache_key(file_key, prefix='b2_url')
    cached_url = cache.get(cache_key)

    if cached_url:
        return cached_url

    b2_client = get_b2_client()
    try:
        url = b2_client.generate_presigned_url('get_object',
                                               Params={'Bucket': settings.B2_BUCKET_NAME,
                                                       'Key': file_key},
                                               ExpiresIn=expires_in)
        
        # Cache the URL (for a shorter time than the expiration)
        cache.set(cache_key, url, timeout=min(expires_in - 60, 3600))  # Cache for the shorter of (expiry - 1 minute) or 1 hour
        
        return url
    except ClientError as e:
        raise Exception(f"Error generating presigned URL: {str(e)}")

def invalidate_b2_file_cache(file_key):
    """Invalidate the cache for a specific file."""
    file_cache_key = get_cache_key(file_key)
    url_cache_key = get_cache_key(file_key, prefix='b2_url')
    cache.delete(file_cache_key)
    cache.delete(url_cache_key)