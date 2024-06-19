from django.contrib import admin
from django.db import connection
import csv
from django.http import HttpResponse
from .models import *


def reset_table_and_identity(modeladmin, request, queryset):
    model = queryset.model
    with connection.cursor() as cursor:
        # Delete all rows from the table
        cursor.execute("DELETE FROM {};".format(model._meta.db_table))
        # Reset the auto-increment sequence
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='{}';".format(model._meta.db_table))

reset_table_and_identity.short_description = "Reset table and identity key"

def save_to_csv(modeladmin, request, queryset):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=query_history.csv'

    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Query', 'Database', 'Query Type', 'Timestamp'])

    for query in queryset:
        writer.writerow([query.id, query.user.username, query.query, query.database, query.query_type, query.timestamp])

    return response
save_to_csv.short_description = 'Save selected queries to CSV'


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')
    list_filter = ('user__is_active', 'user__is_staff')

class DatabaseUploadAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'uploaded_at', 'hostType', 'size')
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

class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'query', 'database', 'query_type', 'timestamp')
    search_fields = ('user__username', 'database')
    list_filter = ('timestamp', 'query_type',)
    actions = [reset_table_and_identity, save_to_csv]

class DatabaseConnectionAdmin(admin.ModelAdmin):
    list_display = ('database_name', 'host', 'port', 'dbname', 'user', 'connection_date')
    search_fields = ('database__name', 'host', 'port', 'dbname', 'user')
    list_filter = ('connection_date',)

    def database_name(self, obj):
        return obj.database.name

    database_name.admin_order_field = 'database__name'
    database_name.short_description = 'Database Name'




admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(DatabaseUpload, DatabaseUploadAdmin)
admin.site.register(DatabaseType)
admin.site.register(APIUsage, APIUsageTable)
admin.site.register(is_allowed_SQL_beta, is_allowed_table)
admin.site.register(QueryHistory, QueryHistoryAdmin)
admin.site.register(DatabaseConnection, DatabaseConnectionAdmin)
