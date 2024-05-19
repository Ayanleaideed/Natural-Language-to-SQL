from django.shortcuts import render, redirect, HttpResponseRedirect
# from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import DatabaseUpload, DatabaseType, APIUsage, is_allowed_SQL_beta
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import sqlite3
import psycopg2
from .utils_func import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum



def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'You have successfully logged in {request.user.username}...')
            return redirect('index')
        else:
            # Check if the user exists to provide a specific error message
            user_exists = User.objects.filter(username=username).exists()
            if user_exists:
                messages.error(request, 'Invalid password. Please try again.')
            else:
                messages.error(request, 'Invalid username. Please try again.')
            return render(request, 'auth/login.html', {'username': username})

    # Show the login page for GET requests
    return render(request, 'auth/login.html',  {})



def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

    
        try:
            # Check if the username already exists to prevent duplication
            if User.objects.filter(username=username).exists():
                messages.warning(request, 'This username has already been taken.')
                return redirect('register')

            # Create new user if username is unique
            user = User.objects.create_user(username=username, password=password)
            user.save()
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('index')
            else:
                messages.error(request, 'Authentication failed. Please try again.')
                return redirect('register')
        except Exception as e:
            messages.error(request, f'Registration failed: {e}')
            return redirect('register')

    return render(request, 'auth/register.html')


    
def logout_user(request):
    username = request.user.username
    logout(request)
    messages.success(request, f'You have been logged out, {username}.')
    return redirect('login_user')
    
@login_required(login_url=login_user)
# Create your views here.
def index(request):
    user = request.user
    if user.username == 'TestUser':
            
        message_from = (
            "This user has limited features. This user is not able to delete any "
            "database but is allowed to delete a list of a maximum of three queries. "
            "The purpose of this is to prevent one anonymous user from deleting this "
            "test database for everybody to test if they don't have a database to test on. "
            "Thank you for understanding."
        )
        messages.warning(request, message_from)
        return render(request, 'loading.html')
    return render(request, 'loading.html')
    
    # return render(request, 'Secret_code.html')




    
@login_required(login_url=login_user)
def query_func(request):
    cur_user = request.user
    databases = DatabaseUpload.objects.filter(user=cur_user)
    
    if request.method == 'POST':
        selected_database_id = request.POST.get('selected_database')
        sql_query = request.POST.get('SQL_text')
        nl_query = request.POST.get('NL_text')

        if 'sql_query' in request.POST:
            
            if selected_database_id and sql_query:
                try:
                    selected_database = DatabaseUpload.objects.get(id=selected_database_id)
                except DatabaseUpload.DoesNotExist:
                    return HttpResponseRedirect('https://http.cat/images/409.jpg')
                
                db_type = DatabaseType.objects.get(id=selected_database.type.id).name 
                db_path = selected_database.file.path
                
                if db_type == 'SQLite':
                    try:
                        query_result_with_headers, column_names = execute_sqlite_query(db_path, sql_query)
                    except sqlite3.DatabaseError as e:
                        messages.error(request, f"Incorrect Query..{e}")
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
                messages.warning(request, 'Make sure to select a database and enter a SQL query.')

        elif 'nl_query' in request.POST:
            if selected_database_id and nl_query:
                try:
                    selected_database = DatabaseUpload.objects.get(id=selected_database_id)
                except DatabaseUpload.DoesNotExist:
                    return HttpResponseRedirect('https://http.cat/images/409.jpg')

                db_type = DatabaseType.objects.get(id=selected_database.type.id).name
                db_path = selected_database.file.path
                sql_query_generated = generate_sql_query(nl_query, databases_context=get_database_schema(db_path))
                
                if db_type == 'SQLite':
                    try:
                        query_result_with_headers, column_names = execute_sqlite_query(db_path, sql_query_generated)
                    except sqlite3.DatabaseError:
                        messages.error(request, "File is not a valid SQLite database.")
                        return render(request, 'query.html', {'databases': databases})
                    except sqlite3.Error as e:
                        messages.error(request, f"SQLite error: {e}")
                        return render(request, 'query.html', {'databases': databases})
                elif db_type == 'PostgreSQL':
                    try:
                        query_result_with_headers, column_names = execute_postgres_query(db_path, sql_query_generated)
                    except psycopg2.DatabaseError:
                        messages.error(request, "Failed to query PostgreSQL database.")
                        return render(request, 'query.html', {'databases': databases})
                    except psycopg2.Error as e:
                        messages.error(request, f"PostgreSQL error: {e}")
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
                messages.warning(request, 'Make sure to select a database and enter a natural language query.')
   
    return render(request, 'query.html', {'databases': databases, })

    
@login_required(login_url=login_user)
def delete_database(request, pk):
    if request.method == 'POST':
        database = DatabaseUpload.objects.get(pk=pk)
        user = request.user
        if database.user == user:
            try:
                database.delete()
                messages.success(request, f'{database.name}: Database deleted successfully')
                return redirect('management')
            except Database.DoesNotExist as e:
                messages.warning(request, f'Error has occurred while deleting database {e}')
        messages.warning(request, f'{database.name}: Your not authorized to delete database')
    database = DatabaseUpload.objects.get(id=pk)
    return render(request, 'confirmation_delete.html', {'db_info': database})


# SQl generator helper functions
@login_required(login_url=login_user)
@csrf_exempt
def chat_submit_view(request):
    if request.method == 'POST':
        user = request.user
        rate_limit_ok, wait_time = APIUsage.check_rate_limit(user, 'submit_code', 10, 3600)
        
        if not rate_limit_ok:
            print(wait_time)
            return JsonResponse({'generated_code': '', 
                                 'messages': f"You have exceeded the rate limit. Please wait Until {get_time(wait_time)}."})
        
        code_text = request.POST.get('code_text')
        context_data = request.POST.get('context_data')

        # Process the code_text and generate a response
        generated_code = get_sql_question_answer(code_text, context_data)
        
        # Log the API usage
        APIUsage.objects.create(user=user, endpoint='submit_code')
        
        return JsonResponse({'generated_code': generated_code, 'messages': ''})
    return render(request, 'chat_submit.html', {})


@login_required(login_url='login_user')
def secret_code(request):
    if request.method == 'POST':
        secret_code = request.POST.get('secret_code')
        code = Alpha_and_beta_test()
        cur_user = request.user
        try:
            is_allowed_user = is_allowed_SQL_beta.objects.get(user=cur_user)
            if secret_code == code and is_allowed_user.Is_allowed:
                messages.warning(request, 'Welcome to the SQL Generation hub. Please be responsible...')
                return redirect('submit_code')
            else:
                messages.warning(request, 'Your code is incorrect. Please type the correct code!')
        except ObjectDoesNotExist:
            messages.warning(request, f'{cur_user.username} not found or Not allowed.')
        except Exception as e:
            messages.warning(request, f'Something went wrong... {e}')
    return render(request, 'secret_code.html', {})





    
@login_required(login_url=login_user)
def management(request):
    cur_user = request.user
    databases = DatabaseUpload.objects.filter(user=cur_user)
    return render(request, 'management.html', {'databases': databases})

    
@login_required(login_url=login_user)
def generate_sql(request):
    # cur_user = request.user
    # is_allowed_user = is_allowed_SQL_beta.objects.get(user=cur_user)
    # if is_allowed_user.Is_allowed:
    #    redirect('secret_code')
    # else:
    messages.info(request, 'This feature is Coming Soon. it will be available july 2024')
    return render(request, 'generate_sql.html', {})




# function to handle the database uploaded files
# @login_required(login_url=)
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

if __name__ == '__main__':
    debug = True

