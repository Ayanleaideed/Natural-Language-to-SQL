
import sqlite3

import mysql.connector
import psycopg2
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import (HOST_CHOICES, APIUsage, DatabaseConnection, DatabaseType,
                     DatabaseUpload, QueryHistory, is_allowed_SQL_beta)
from .utils_func import *


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
    query_history = QueryHistory.objects.filter(user=cur_user).order_by('-timestamp')[:4]


    if request.method == 'POST':
        selected_database_id = request.POST.get('selected_database')
        sql_query = request.POST.get('SQL_text')
        nl_query = request.POST.get('NL_text')

        if 'sql_query' in request.POST:

            if selected_database_id and sql_query:
                try:
                    selected_database = DatabaseUpload.objects.get(id=selected_database_id)
                except DatabaseUpload.DoesNotExist:
                    messages.warning(request, 'Database %s does not exist ' % selected_database_id)
                    return redirect(query_func(request))

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
                        db_path = selected_database
                        query_result_with_headers, column_names = execute_postgres_query(request.user, db_path, sql_query)
                    except psycopg2.DatabaseError:
                        messages.error(request, "Failed to query PostgreSQL database.")
                        return render(request, 'query.html', {'databases': databases})
                elif db_type == 'MySQL':
                    try:
                        db_path = selected_database
                        query_result_with_headers, column_names = execute_mysql_query(request.user, db_path, sql_query)
                    except psycopg2.DatabaseError:
                        messages.error(request, "Failed to query PostgreSQL database.")
                        return render(request, 'query.html', {'databases': databases})
                else:
                    messages.error(request, "Unsupported database type.")
                    return render(request, 'query.html', {'databases': databases})
                queryType = "SQL"
                query = sql_query

                # save the query to history models
                if QueryHistory.objects.filter(Q(query=query.upper()) | Q(query=query.lower())).exists():
                    pass
                else:
                    q = QueryHistory.objects.create(
                        user=request.user,
                        query=query,
                        database=selected_database,
                        query_type=queryType
                        )
                    q.save()
                return render(request, 'query_results.html', {
                    'databases': databases,
                    'query_result': query_result_with_headers,
                    'column_names': column_names,
                    'queryType': queryType,
                    'query': query
                })
            else:
                messages.warning(request, 'Make sure to select a database and enter a SQL query.')

        elif 'nl_query' in request.POST:
            if selected_database_id and nl_query:
                try:
                    selected_database = DatabaseUpload.objects.get(id=selected_database_id)
                except DatabaseUpload.DoesNotExist:
                    # return HttpResponseRedirect('https://http.cat/images/409.jpg')
                    return redirect(query)

                db_type = DatabaseType.objects.get(id=selected_database.type.id).name
                db_path = selected_database.file.path
                if db_type == 'SQLite':
                    sql_query_generated = generate_sql_query(db_type, nl_query, databases_context=get_database_schema(db_type, db_path))
                elif db_type == "PostgreSQL":
                    sql_query_generated = generate_sql_query(db_type, nl_query, databases_context=get_database_schema(db_type, selected_database))
                elif db_type == 'MySQL':
                    sql_query_generated = generate_sql_query(db_type, nl_query, databases_context=get_database_schema(db_type, selected_database))





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
                        db_path = selected_database
                        query_result_with_headers, column_names = execute_postgres_query(request.user, db_path, sql_query_generated)
                    except psycopg2.DatabaseError:
                        messages.error(request, "Failed to query PostgreSQL database.")
                        return render(request, 'query.html', {'databases': databases})
                    except psycopg2.Error as e:
                        messages.error(request, f"PostgreSQL error: {e}")
                        return render(request, 'query.html', {'databases': databases})
                elif db_type == 'MySQL':
                    try:
                        print(sql_query_generated)
                        db_path = selected_database
                        query_result_with_headers, column_names = execute_mysql_query(request.user, db_path, sql_query_generated)
                    except psycopg2.DatabaseError:
                        messages.error(request, "Failed to query PostgreSQL database.")
                        return render(request, 'query.html', {'databases': databases})
                    except psycopg2.Error as e:
                        messages.error(request, f"PostgreSQL error: {e}")
                        return render(request, 'query.html', {'databases': databases})
                else:
                    messages.error(request, "Unsupported database type.")
                    return render(request, 'query.html', {'databases': databases})
                queryType = "NL"
                query = sql_query_generated

                # save the query to history models
                if QueryHistory.objects.filter(Q(query=query.upper()) | Q(query=query.lower())).exists():
                    pass
                else:
                    q = QueryHistory.objects.create(
                        user=request.user,
                        query=query,
                        database=selected_database,
                        query_nl_text=nl_query,
                        query_type=queryType
                        )
                    q.save()

                return render(request, 'query_results.html', {
                    'databases': databases,
                    'query_result': query_result_with_headers,
                    'column_names': column_names,
                    'queryType': queryType,
                    'query': query
                })
            else:
                messages.warning(request, 'Make sure to select a database and enter a natural language query.')
    return render(request, 'query.html', {'databases': databases, 'query_history': query_history})


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
# @csrf_exempt
def chat_submit_view(request):
    user = request.user
    try:
        # Check if the user is allowed to access SQL generation
        is_auth_user_beta = is_allowed_SQL_beta.objects.get(user=user)
        if not is_auth_user_beta.Is_allowed:
          # Redirect to home or some other page if not allowed
            return redirect('/')
    except is_allowed_SQL_beta.DoesNotExist:
        messages.warning(request, 'You do not have permission to access this page!')
        return redirect('/')
    # Check if secret code validation is done
    if not request.session.get('secret_code_validated', False):
      # Redirect to secret_code view if not validated
        return redirect('secret_code')


    if request.method == 'POST':
        # Check rate limit
        rate_limit_ok, wait_time = APIUsage.check_rate_limit(user, 'submit_code', 20, 3600)
        if not rate_limit_ok:
            return JsonResponse({
                'generated_code': '',
                'messages': f"You have exceeded the rate limit. Please wait until {get_time(wait_time)}."
            })

        code_text = request.POST.get('code_text')
        context_data = request.POST.get('context_data')

        # Process the code_text and generate a response ( using get_sql_question_answer function from the utils)
        generated_code = get_sql_question_answer(code_text)

        if not generated_code:
            messages.error(request, 'Could not generate an answer for this request...')
            return JsonResponse({'generated_code': '', 'messages': generated_code})

        # Log the API usage
        APIUsage.objects.create(user=user, endpoint='submit_code')

        return JsonResponse({'generated_code': generated_code, 'messages': ''})

    return render(request, 'chat_submit.html', {})


@login_required(login_url='/login/')
def secret_code(request):
    if request.method == 'POST':
        secret_code = request.POST.get('secret_code')
        code = Alpha_and_beta_test()
        cur_user = request.user
        try:
            is_allowed_user = is_allowed_SQL_beta.objects.get(user=cur_user)
            if secret_code == code and is_allowed_user.Is_allowed:
                # Set a session variable to mark that secret code validation is done
                request.session['secret_code_validated'] = True
                messages.success(request, 'Welcome to the SQL Generation hub. Please be responsible...')
                return redirect('submit_code')  # Redirect to the submit_code if successful entry
            else:
                messages.warning(request, 'Your code is incorrect. Please type the correct code!')
        except ObjectDoesNotExist:
            messages.warning(request, f'{cur_user.username} not found or not allowed.')

        except Exception as e:
            messages.warning(request, f'Something went wrong... {e}')

    return render(request, 'secret_code.html', {})



@login_required(login_url=login_user)
def management(request):
    cur_user = request.user
    dbObj = DatabaseType.objects.all()
    cur_db_type = [db.name for db in dbObj if db.name != 'SQLite']
    databases = DatabaseUpload.objects.filter(user=cur_user)
    return render(request, 'management.html', {'databases': databases, 'db_host': cur_db_type})


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
        if 'database_file' in request.FILES or 'database_name' in request.POST:
            try:
                # database_file = request.FILES['database_file']
                database_file = request.FILES.get('database_file', None)
                database_name = request.POST.get('database_name')
                database_type = request.POST.get('database_type')
                hostType = request.POST.get('hostType')
                user = request.user

                database_type = DatabaseType.objects.get(id=database_type)

                # Save the file using the custom upload path
                database_upload = DatabaseUpload(user=user, name=database_name, file=database_file, type=database_type, hostType=hostType)
                database_upload.save()

                messages.success(request, 'Database uploaded successfully!')
                return redirect('management')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
        else:
            messages.error(request, 'No file uploaded. Please try again.')

    Database_type = DatabaseType.objects.all()
    db_hosts = HOST_CHOICES

    return render(request, 'upload_database.html', {'Database_type': Database_type, 'db_hosts': db_hosts})



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

def execute_postgres_query(user, db_path, query):

    # PostgreSQL connection details
    #find the database object
    db_conn = DatabaseUpload.objects.get(user=user, id=db_path.id)
    # return a database configuration object based on the given database object
    db_conn = DatabaseConnection.objects.get(database=db_conn)
    # connection to host database
    conn = psycopg2.connect(
            dbname=db_conn.dbname,
            user= db_conn.user,
            password=db_conn.password,
            host=db_conn.host,
            port=db_conn.port
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

def execute_mysql_query(user, db_path, query):
    # MySQL connection details
    db_conn = DatabaseUpload.objects.get(user=user, id=db_path.id)
    db_conn = DatabaseConnection.objects.get(database=db_conn)
    conn = mysql.connector.connect(
        user=db_conn.user,
        password=db_conn.password,
        host=db_conn.host,
        database=db_conn.dbname,
        port=db_conn.port
    )

    cursor = conn.cursor()
    cursor.execute(query)
    query_result = cursor.fetchall()
    column_names = cursor.column_names
    query_result_with_headers = [
        {column_names[i]: value for i, value in enumerate(row)}
        for row in query_result
    ]
    conn.close()
    return query_result_with_headers, column_names



# function to handle PostgreSQL and MySQL Connections
def db_connection(request, id):
    try:
        # Retrieve the DatabaseUpload object if it belongs to the current user
        dbObject = DatabaseUpload.objects.get(user=request.user, id=id)
        try:
            previewConn = DatabaseConnection.objects.get(database=dbObject)
        except DatabaseConnection.DoesNotExist:
            previewConn = {}

    except DatabaseUpload.DoesNotExist:
        messages.error(request, "You are not authorized to access this database.")
        return redirect(management)


    if request.method == 'POST':
        host = request.POST.get('host')
        port = request.POST.get('port')
        dbname = request.POST.get('dbname')
        user = request.POST.get('user')
        password = request.POST.get('password')

        # Determine the database type
        if dbObject.type.name == 'PostgreSQL':
            try:
                # Establish the PostgreSQL connection
                conn = psycopg2.connect(
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=host,
                    port=port
                )
                messages.success(request, 'Database connection established successfully...')
                conn.close()
                # if the connection is established successfully then we go ahead and save the connection string for later access
                cur_db_obj = DatabaseUpload.objects.get(user=request.user, id=id)
                # check if this database already exists
                existing_db = DatabaseConnection.objects.filter(database=cur_db_obj)

                if existing_db.exists():
                    existing_db.update(
                        host=host,
                        port=port,
                        dbname=dbname,
                        user=user,
                        password=password
                    )
                    messages.success(request, 'Database connection has been updated successfully')
                else:
                    new_db = DatabaseConnection(
                        database=cur_db_obj,
                        host=host,
                        port=port,
                        dbname=dbname,
                        user=user,
                        password=password
                    )
                    new_db.save()
                    messages.success(request, 'New database connection has been created successfully')


                return redirect(management)
            except psycopg2.OperationalError as e:
                message = f"Connection failed: {e}"
                messages.error(request, f'We encountered an error while connecting: {message}')
                return redirect(management)

        elif dbObject.type.name == 'MySQL':
            try:
                # Establish the MySQL connection
                conn = mysql.connector.connect(
                    user=user,
                    password=password,
                    host=host,
                    database=dbname,
                    port=port
                )
                messages.success(request, 'Database connection established successfully...')
                conn.close()
                # if the connection is established successfully then we go ahead and save the connection string for later access
                cur_db_obj = DatabaseUpload.objects.get(user=request.user, id=id)
                # check if this database already exists
                existing_db = DatabaseConnection.objects.filter(database=cur_db_obj)

                if existing_db.exists():
                    existing_db.update(
                        host=host,
                        port=port,
                        dbname=dbname,
                        user=user,
                        password=password
                    )
                    messages.success(request, 'Database connection has been updated successfully')
                else:
                    new_db = DatabaseConnection(
                        database=cur_db_obj,
                        host=host,
                        port=port,
                        dbname=dbname,
                        user=user,
                        password=password
                    )
                    new_db.save()
                    messages.success(request, 'New database connection has been created successfully')

            except mysql.connector.Error as e:
                message = f"Connection failed: {e}"
                messages.error(request, f'We encountered an error while connecting: {message}')
            return redirect(management)

    return render(request, 'database-connections.html', {'dbObject': dbObject, 'previewConn': previewConn})





def games(request):
    context = {}
    if request.method == 'POST':
        user_answer = request.POST.get('user_answer')
        previous_question = request.POST.get('previous_question')
        user_performance = request.POST.get('user_performance') == 'True'

        # Check if previous_question is empty or None, indicating the start of the game
        if not previous_question:
            # Start with an easy question
            initial_question, initial_difficulty = get_next_sql_question('', '', True)
            context.update({'next_question': initial_question, 'difficulty': initial_difficulty})
        else:
            # Continue with the next question based on user's performance
            response = get_next_sql_question(previous_question, user_answer, user_performance, request.user.username)
            context.update({'next_question': response[0], 'difficulty': response[1]})
    else:
        # Initial welcome message
        context.update({'welcome_message': f"{request.user.username}, welcome! Do you want to play the SQL game?"})

    return render(request, 'games.html', context)





if __name__ == '__main__':
    debug = True

