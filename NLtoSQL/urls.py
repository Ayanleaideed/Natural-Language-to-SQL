
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path("", views.loading, name='index'),
    path("", views.index, name='index'),
    path('query/', views.query_func, name='query'),
    path('management/', views.management, name='management'),
    path('generate/', views.generate_sql, name='generate_sql'),
    path('upload_database/', views.upload_database, name='upload_database'),
    path('code/', views.secret_code, name='secret_code'),
    path('submit_chat/', views.chat_submit_view, name='submit_code'),
    path('delete_database/<int:pk>/', views.delete_database, name='delete_database'),
    path('login_user/', views.login_user, name='login_user'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('register/', views.register, name='register'),
    path('connection/<int:id>', views.db_connection, name='db_connection'),
    path('database-schema/<int:database_id>/', views.database_schema, name='database_schema'),
    path('games/', views.games, name='games'),

]
