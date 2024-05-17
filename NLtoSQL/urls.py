
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
    path('submit_code/', views.submit_code_view, name='submit_code'),
    
]
