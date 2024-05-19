from django.contrib import admin
from .models import UserProfile, DatabaseUpload,  DatabaseType, APIUsage, is_allowed_SQL_beta

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')
    list_filter = ('user__is_active', 'user__is_staff')

class DatabaseUploadAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'uploaded_at', 'size')
    search_fields = ('name', 'user__username')
    list_filter = ('uploaded_at',)
    readonly_fields = ('size',)


class APIUsageTable(admin.ModelAdmin):
    actions = ['delete_selected'] 
    list_display = ('user', 'endpoint', 'timestamp')
    search_fields = ('user__username',)
    list_filter = ('user',)
    readonly_fields = ('timestamp',)
    
class is_allowed_table(admin.ModelAdmin):
    list_display = ('user', 'Is_allowed')
    search_fields = ('user__username',)
    list_filter = ('user',)
    
    


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(DatabaseUpload, DatabaseUploadAdmin)
admin.site.register(DatabaseType)
admin.site.register(APIUsage, APIUsageTable)
admin.site.register(is_allowed_SQL_beta, is_allowed_table)

# DATABASE_TYPES = [
#         ('sqlite', 'SQLite'),
#         ('postgresql', 'PostgreSQL'),
#         ('mssql', 'MS SQL Server'),
#     ]