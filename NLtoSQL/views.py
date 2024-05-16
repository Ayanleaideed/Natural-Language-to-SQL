from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from .models import DatabaseUpload, DatabaseType
from django.contrib import messages



# Create your views here.
def index(request):
  name = 'Doozy'
  return render(request, 'loading.html', {'name': name})



def query_func(request):
  messages.success(request, 'test message')
  return render(request, 'query.html', {})


def management(request):
    databases = DatabaseUpload.objects.all()
    for db in databases:
        print('name', db.name)
    return render(request, 'management.html', {'databases': databases})


def generate_sql(request):
  return render(request, 'generate_sql.html', {})



# function to handle the database uploaded files
# @login_required
def upload_database(request):
    if request.method == 'POST':
        if 'database_file' in request.FILES:
            try:
                database_file = request.FILES['database_file']
                database_name = request.POST.get('database_name')
                database_type = request.POST.get('database_type')
                user = request.user

                database_type = DatabaseType.objects.get(id=database_type)

                # Save the file using the custom upload path
                database_upload = DatabaseUpload(user=user, name=database_name, file=database_file, type=database_type)
                database_upload.save()

                messages.success(request, 'Database uploaded successfully!')
                return redirect('management')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
        else:
            messages.error(request, 'No file uploaded. Please try again.')
           
    Database_type = DatabaseType.objects.all()

    return render(request, 'upload_database.html', {'Database_type': Database_type})




if __name__ == '__main__':
  debug = True