from django.contrib import admin
from .models import UserProfile, DatabaseUpload,  DatabaseType

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')
    list_filter = ('user__is_active', 'user__is_staff')

class DatabaseUploadAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'uploaded_at', 'size')
    search_fields = ('name', 'user__username')
    list_filter = ('uploaded_at',)
    readonly_fields = ('size',)
    


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(DatabaseUpload, DatabaseUploadAdmin)
admin.site.register(DatabaseType)


# DATABASE_TYPES = [
#         ('sqlite', 'SQLite'),
#         ('postgresql', 'PostgreSQL'),
#         ('mssql', 'MS SQL Server'),
#     ]