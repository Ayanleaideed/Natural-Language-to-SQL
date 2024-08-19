from django.core.cache import cache
from django.conf import settings
import hashlib
import json
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from .models import DatabaseUpload
from .utils_func import get_database_schema
from django.core import serializers




# Cache timeout (e.g., 1 hour)
CACHE_TIMEOUT = getattr(settings, 'DATABASE_CACHE_TIMEOUT', 3600 ) # default time ll' be 1 hour

def get_cache_key(user_id, action):
    """Generate a unique cache key for a user and action."""
    return f"user_{user_id}_{action}"

def get_cached_user_databases(user):
    cache_key = get_cache_key(user.id, 'databases')
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        # If not in cache, fetch from database
        databases = DatabaseUpload.objects.filter(user=user).select_related('type')
        # Serialize the queryset
        serialized_data = serializers.serialize('json', databases, use_natural_foreign_keys=True)
        # Cache the serialized data
        cache.set(cache_key, serialized_data, timeout=3600)
        return databases
    else:
        # Deserialize the cached data
        deserialized_objects = list(serializers.deserialize('json', cached_data))
        return [obj.object for obj in deserialized_objects]



def invalidate_user_databases_cache(user):
    """Invalidate the cache for a user's databases."""
    cache_key = get_cache_key(user.id, 'databases')
    cache.delete(cache_key)

def get_cached_database_schema(user, database_id):
    """Retrieve or cache database schema."""
    cache_key = get_cache_key(user.id, f'schema_{database_id}')
    cached_schema = cache.get(cache_key)

    if cached_schema is None:
        try:
            database = DatabaseUpload.objects.get(id=database_id, user=user)
            schema = get_database_schema(database.type.name, database)
            cache.set(cache_key, json.dumps(schema), CACHE_TIMEOUT)
        except DatabaseUpload.DoesNotExist:
            return None
    else:
        schema = json.loads(cached_schema)

    return schema

def invalidate_database_schema_cache(user, database_id):
    """Invalidate the cache for a database schema."""
    cache_key = get_cache_key(user.id, f'schema_{database_id}')
    cache.delete(cache_key)



# Middleware to update cache on database modifications
from django.utils.deprecation import MiddlewareMixin

class DatabaseCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated:
            if request.path.startswith('/upload_database') or request.path.startswith('/delete_database'):
                invalidate_user_databases_cache(request.user)
        return response

    

# Function to invalidate the cache when permissions change
def invalidate_sql_beta_cache(user_id):
    cache_key = get_cache_key(user_id, 'sql_beta_access')
    cache.delete(cache_key)

