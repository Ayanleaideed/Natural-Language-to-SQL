from django.shortcuts import render, redirect, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from .models import DatabaseUpload, DatabaseType
from django.contrib import messages
import sqlite3
import psycopg2
from .utils import generate_sql_query, get_database_schema



# Create your views here.
def index(request):
    message_from = (
        "This user has limited features. This user is not able to delete any "
        "database but is allowed to delete a list of a maximum of three queries. "
        "The purpose of this is to prevent one anonymous user from deleting this "
        "test database for everybody to test if they don't have a database to test on. "
        "Thank you for understanding."
    )
    messages.warning(request, message_from)
    return render(request, 'loading.html')
    # return render(request, 'Secret_code.html')
    



def query_func(request):
    cur_user = request.user
    databases = DatabaseUpload.objects.filter(user=cur_user)
    
    if request.method == 'POST':
        selected_database_id = request.POST.get('selected_database')
        sql_query = request.POST.get('SQL_text')
        nl_query = request.POST.get('NL_text')

        if 'sql_query' in request.POST:
            if selected_database_id:
                try:
                    selected_database = DatabaseUpload.objects.get(id=selected_database_id)
                except DatabaseUpload.DoesNotExist:
                    return HttpResponseRedirect('https://http.cat/images/409.jpg')
                
                db_type = DatabaseType.objects.get(id=selected_database.type.id).name 
                db_path = selected_database.file.path
                
                if db_type == 'SQLite':
                    try:
                        query_result_with_headers, column_names = execute_sqlite_query(db_path, sql_query)
                    except sqlite3.DatabaseError:
                        messages.error(request, "File is not a valid SQLite database.")
                        return render(request, 'query.html', {'databases': databases})
                elif db_type == 'PostgreSQL':
                    try:
                        query_result_with_headers, column_names = execute_postgres_query(db_path, sql_query)
                    except psycopg2.DatabaseError:
                        messages.error(request, "Failed to query PostgreSQL database.")
                        return render(request, 'query.html', {'databases': databases})
                else:
                    messages.error(request, "Unsupported database type.")
                    return render(request, 'query.html', {'databases': databases})

                return render(request, 'query_results.html', {
                    'databases': databases,
                    'query_result': query_result_with_headers,
                    'column_names': column_names
                })
            else:
                messages.warning(request, 'Make sure to select a database or upload a new one!')

        elif 'nl_query' in request.POST:
            if nl_query:
                if selected_database_id:
                
                    try:
                        selected_database = DatabaseUpload.objects.get(id=selected_database_id)
                    except DatabaseUpload.DoesNotExist:
                        return HttpResponseRedirect('https://http.cat/images/409.jpg')

                    db_type = DatabaseType.objects.get(id=selected_database.type.id).name
                    db_path = selected_database.file.path
                    # print(get_database_schema(db_path))
                    sql_query_generated = generate_sql_query(nl_query, databases_context=get_database_schema(db_path))
                    
                    if db_type == 'SQLite':
                        try:
                            query_result_with_headers, column_names = execute_sqlite_query(db_path, sql_query_generated)
                        except sqlite3.DatabaseError:
                            messages.error(request, "File is not a valid SQLite database.")
                            return render(request, 'query.html', {'databases': databases})
                    elif db_type == 'PostgreSQL':
                        try:
                            query_result_with_headers, column_names = execute_postgres_query(db_path, sql_query_generated)
                        except psycopg2.DatabaseError:
                            messages.error(request, "Failed to query PostgreSQL database.")
                            return render(request, 'query.html', {'databases': databases})
                    else:
                        messages.error(request, "Unsupported database type.")
                        return render(request, 'query.html', {'databases': databases})

                    return render(request, 'query_results.html', {
                        'databases': databases,
                        'query_result': query_result_with_headers,
                        'column_names': column_names
                    })
                else:
                    messages.warning(request, 'Make sure to select a database or upload a new one!')

    return render(request, 'query.html', {'databases': databases})
def execute_sqlite_query(db_path, query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    query_result = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    query_result_with_headers = [
        {column_names[i]: value for i, value in enumerate(row)}
        for row in query_result
    ]
    conn.close()
    return query_result_with_headers, column_names

def execute_postgres_query(db_path, query):
    # Replace these with your PostgreSQL connection details
    DB_NAME = 'your_db_name'
    DB_USER = 'your_db_user'
    DB_PASSWORD = 'your_db_password'
    DB_HOST = 'your_db_host'
    DB_PORT = 'your_db_port'
    
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    cursor.execute(query)
    query_result = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    query_result_with_headers = [
        {column_names[i]: value for i, value in enumerate(row)}
        for row in query_result
    ]
    conn.close()
    return query_result_with_headers, column_names




def management(request):
    cur_user = request.user
    databases = DatabaseUpload.objects.filter(user=cur_user)
    return render(request, 'management.html', {'databases': databases})


def generate_sql(request):
  messages.info(request, 'This feature is Coming Soon. it will be available july 2024')
  return render(request, 'generate_sql.html', {})

def secret_code(request):
    return render(request, 'secret_code.html', {})


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

