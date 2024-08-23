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

# from django.views.decorators.csrf import csrf_exempt
from dataclasses import dataclass
from .models import (HOST_CHOICES, APIUsage, DatabaseConnection, DatabaseType,
                     DatabaseUpload, QueryHistory, is_allowed_SQL_beta, DatabasePermissions)
# utils functions
from .utils_func import * 
from .b2_utils import *
from .cache_system import * 





def login_user(request):
    messages.info(
    request,
        (
            "For those who want to test, you can use the following credentials:\n"
            "Username: [TestUser]:"
            " Password: [TestUser]"
            "This user can try the app with pre-uploaded sample databases. "
            "NOTE: that this user has limited permissions: it cannot drop or delete tables, "
            "but it can create new tables or Select. Please be responsible.😊😊"
        )
    )
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

# demo login for test users 
def demoLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in and redirect to the index page
            login(request, user)
            return redirect('index')
        else:
            # Return an error message if authentication fails
            error_message = "Invalid username or password"
            messages.error(request, error_message)
            return render(request, 'auth/demoLogin.html', {'error_message': error_message})
    
    # If the request method is GET, render the login page
    return render(request, 'auth/demoLogin.html')



def register(request):
    messages.info(
    request,
    (
        "For those who want to test, you can use the following credentials:\n"
        "Username: [TestUser]:"
        " Password: [TestUser]"
        "This user can try the app with pre-uploaded sample databases. "
        "NOTE: that this user has limited permissions: it cannot drop or delete tables, "
        "but it can create new tables or Select. Please be responsible.😊😊"
    )
    )
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        #clear the data 
        username = username.strip()
        password = password.strip()

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
    if 'secret_code_validated' in request.session:
        del request.session['secret_code_validated']
    username = request.user.username
    logout(request)
    messages.success(request, f'You have been logged out, {username}.')
    return redirect('login_user')


@login_required(login_url=login_user)
def index(request):
    user = request.user
    if user.username == 'TestUser':
        # Filter DatabasePermissions objects where at least one permission is True
        user_permissions = DatabasePermissions.objects.filter(
            Q(can_select=True) | Q(can_insert=True) | Q(can_update=True) | Q(can_delete=True),
            user=user )
        # Generate the message with user permissions
        permissions_list = ', '.join([
            perm for perm in ['select', 'insert', 'update', 'delete']
            if getattr(user_permissions.first(), f'can_{perm}', False)
        ])

        message_from = (
            "This user has limited features. This user is not able to delete any "
            "database but is allowed to delete a list of a maximum of three queries. "
            "The purpose of this is to prevent one anonymous user from deleting this "
            "test database for everybody to test if they don't have a database to test on. "
            "Thank you for understanding. "
            f"Here are the user permissions that are allowed for this Account: {permissions_list.upper()}"
        )
        messages.warning(request, message_from)
    # TODO: add new new feature to here
    upComingFeatures = [
    {'name': 'SQL Game', 'description': 'SQL Game for practicing upcoming interviews or just learning in general 📖👍'},
    # {'name': 'Python Quiz', 'description': 'Python Quiz to test your skills and knowledge 🧠💡'},
    {'name': 'Code Challenges', 'description': 'A series of code challenges to improve your problem-solving skills 🏆💻'},
    {'name': 'Database Simulator', 'description': 'Simulate database operations and queries for hands-on experience 💾🔍'}
    ]

    return render(request, 'loading.html' ,{'upComingFeatures': upComingFeatures} )

    # return render(request, 'Secret_code.html')



@dataclass
class Query_populate:
    type: str = None
    val: str = None
    db: int = -1

    @classmethod
    def from_session(cls, session):
        return cls(
            type=session.get('type', None),
            val=session.get('val', None),
            db=session.get('selected_db', -1)
        )
        
        

# main function to handle any queries sections and Traffic directions
@login_required(login_url=login_user)
def query_func(request):
    cur_user = request.user
    databases = get_cached_user_databases(cur_user)
    
    query_history_cache_key = get_cache_key(cur_user.id, 'query_history')
    query_history = cache.get(query_history_cache_key)
    
    if query_history is None:
        query_history = list(QueryHistory.objects.filter(user=cur_user).order_by('-timestamp')[:4].values())
        cache.set(query_history_cache_key, query_history, timeout=300)  # Cache for 5 minutes

    query_populate = Query_populate().from_session(request.session)

    if request.method == 'POST':
        result = handle_post_request(request, databases)
        # Invalidate query history cache after a new query
        cache.delete(query_history_cache_key)
        return result

    query_populate = Query_populate(
        type=request.session.get('type'),
        val=request.session.get('val'),
        db=int(request.session.get('selected_db', -1))
    )
    
    return render(request, 'query.html', {
        'databases': databases,
        'query_history': query_history,
        'query_populate': query_populate
    })

class Query_populate:
    def __init__(self, type=None, val=None, db=-1):
        self.type = type
        self.val = val
        self.db = db

    @classmethod
    def from_session(cls, session):
        return cls(
            type=session.get('type'),
            val=session.get('val'),
            db=session.get('selected_db', -1)
        )

    
# The main helper function to handle sql and nl queries
def handle_post_request(request, databases):
    selected_database_id = request.POST.get('selected_database')
    sql_query = request.POST.get('SQL_text')
    nl_query = request.POST.get('NL_text')

    update_session(request, sql_query, nl_query, selected_database_id)

    if 'sql_query' in request.POST:
        return handle_sql_query(request, databases, selected_database_id, sql_query)
    elif 'nl_query' in request.POST:
        return handle_nl_query(request, databases, selected_database_id, nl_query)

    messages.warning(request, 'Invalid request type.')
    return redirect(query_func)

# function to update the session for ui 
def update_session(request, sql_query, nl_query, selected_database_id):
    if sql_query:
        request.session['selected_db'] = -1
        request.session['val'] = sql_query.strip()
        request.session['type'] = 'sql_query'
    elif nl_query:
        request.session['val'] = nl_query.strip()
        request.session['type'] = 'nl_query'
        request.session['selected_db'] = -1

    if selected_database_id:
        request.session['selected_db'] = selected_database_id

# helper function to handle nl queries for the main query_fun 
def handle_sql_query(request, databases, selected_database_id, sql_query):
    if not selected_database_id or not sql_query:
        messages.warning(request, 'Make sure to select a database and enter a SQL query.')
        return redirect(query_func)

    try:
        selected_database = DatabaseUpload.objects.get(id=selected_database_id)
    except DatabaseUpload.DoesNotExist:
        messages.warning(request, f'Database {selected_database_id} does not exist.')
        return redirect(query_func)

    db_type = selected_database.type.name
    query_result, column_names, action = execute_query(db_type, request.user, selected_database, sql_query)

    if action:
        messages.success(request, f"The database action: {action.type.upper()} was successfully: {action.val}")

    save_query_history(request.user, sql_query, selected_database, "SQL")


    return render_query_results(request, databases, query_result, column_names, "SQL", sql_query)

# helper function to handle nl queries for the main query_fun 
def handle_nl_query(request, databases, selected_database_id, nl_query):
    if not selected_database_id or not nl_query:
        messages.warning(request, 'Make sure to select a database and enter a natural language query.')
        return redirect(query_func)

    try:
        selected_database = DatabaseUpload.objects.get(id=selected_database_id)
        # double check that the database is uploaded by this current user
        if not request.user.id == selected_database.user.id:
            messages.error('Your not authorized for this database')
            raise Exception('You are not authorized for this database')
    except DatabaseUpload.DoesNotExist:
        messages.warning(request, f'Database {selected_database_id} does not exist.')
        return redirect(query_func)

    db_type = selected_database.type.name
    if db_type == 'SQLite':
        db_path = selected_database.file.path
        db_schema = get_database_schema(db_type, db_path)
    else:
        db_schema = get_database_schema(db_type, selected_database)
    sql_query_generated = generate_sql_query(db_type, nl_query, databases_context=db_schema)
     # Log the API usage
    APIUsage.objects.create(user=request.user, endpoint='nl_query+query_func', user_input_request_context=nl_query, model_response=sql_query_generated)

    query_result, column_names, action = execute_query(db_type, request.user, selected_database, sql_query_generated)

    if action:
        messages.success(request, f"The database action: {action.type.upper()} was successfully: {action.val}")

    save_query_history(request.user, sql_query_generated, selected_database, "NL", nl_query)

    return render_query_results(request, databases, query_result, column_names, "NL", sql_query_generated)

# Helper function to handle databases execution for the main query function
def execute_query(db_type, user, database, query):
    temp_file = None
    try:
        if db_type == 'SQLite':
            if database.hostType == 'cloud':
                file_content = download_from_b2(database.b2_file_key)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite')
                temp_file.write(file_content.getvalue())
                temp_file.close()
                file_path = temp_file.name
            else:
                file_path = database.file.path
            
            result, column_names, action = execute_sqlite_query(user, file_path, query)
        
        elif db_type == 'PostgreSQL':
            result, column_names, action = execute_postgres_query(user, database, query)
        
        elif db_type == 'MySQL':
            result, column_names, action = execute_mysql_query(user, database, query)
            action = None
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        return result, column_names, action

    finally:
        # Clean up temporary file if it was created
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except PermissionError:
                # If we can't delete the file immediately, we'll leave it for the OS to clean up
                pass

# helper function to save the query for Use experience for query history
def save_query_history(user, query, database, query_type, nl_query=None):
    if not QueryHistory.objects.filter(query__iexact=query).exists():
        QueryHistory.objects.create(
            user=user,
            query=query,
            database=database,
            query_type=query_type,
            query_nl_text=nl_query
        )
        
# helper function to handel result rending to the frontend/interface table for the main query_fun
def render_query_results(request, databases, query_result, column_names, query_type, query, action=None):
    if not query_result:
        query_result = [{"No results": "No results were returned..."}]

    if column_names is None and action is None:
        messages.warning(request, query_result)
        return redirect(query_func)

    if len(query) > 100:
        query = 'Query is too big to Display'

    return render(request, 'query_results.html', {
        'databases': databases,
        'query_result': query_result,
        'column_names': column_names,
        'queryType': query_type,
        'query': query
    })

# views to handle database deletion
@login_required(login_url='login_user')
def delete_database(request, pk):
    try:
        database = DatabaseUpload.objects.get(pk=pk)
    except DatabaseUpload.DoesNotExist:
        messages.error(request, "Database not found.")
        return redirect('management')

    if request.method == 'POST':
        user_confirmation_password = request.POST.get('password')
        if database.user != request.user:
            messages.warning(request, f'{database.name}: You are not authorized to delete this database')
            return redirect('management')
        
        if authenticate(username=request.user.username, password=user_confirmation_password):
            try:
                # The delete() method now handles both B2 and database deletion
                database.delete()
                invalidate_user_databases_cache(request.user)
                
                messages.success(request, f'{database.name}: Database deleted successfully')
                return redirect('management')
            except Exception as e:
                messages.error(request, f'Error occurred while deleting database: {str(e)}')
        else:
            messages.warning(request, 'Invalid password')
    
    return render(request, 'confirmation_delete.html', {'db_info': database})


# SQl generator helper functions
@login_required(login_url='/login/')
def chat_submit_view(request):
    user = request.user
    cache_key = get_cache_key(user.id, 'sql_beta_access')
    
    # Try to get the permission status from cache
    is_allowed_user = cache.get(cache_key)
    
    if is_allowed_user is None:
        # If not in cache, check the database
        try:
            is_allowed_user = is_allowed_SQL_beta.objects.get(user=user).Is_allowed
            # Cache the result for future requests (e.g., for 1 hour)
            cache.set(cache_key, is_allowed_user, 3600)
        except is_allowed_SQL_beta.DoesNotExist:
            is_allowed_user = False
            # Cache the negative result as well
            cache.set(cache_key, False, 3600)

    if not is_allowed_user:
        messages.warning(request, 'You do not have permission to access this page!')
        return redirect('/')

    if not request.session.get('secret_code_validated', False):
        return redirect('secret_code')

    if request.method == 'POST':
        rate_limit_ok, wait_time = APIUsage.check_rate_limit(user, 'submit_code', 20, 3600)
        if not rate_limit_ok:
            return JsonResponse({
                'generated_code': '',
                'messages': f"You have exceeded the rate limit. Please wait until {get_time(wait_time)}."
            })

        code_text = request.POST.get('code_text')
        generated_code = get_sql_question_answer(code_text)

        if not generated_code:
            messages.error(request, 'Could not generate an answer for this request...')
            return JsonResponse({'generated_code': '', 'messages': generated_code})
        
        APIUsage.objects.create(user=user, endpoint='submit_code', user_input_request_context=code_text, model_response=generated_code)
        return JsonResponse({'generated_code': generated_code, 'messages': ''})

    return render(request, 'chat_submit.html', {})


# Views to handle the secret code for beta test
@login_required(login_url='login_user')
def secret_code(request):
    cur_user = request.user
    cache_key = get_cache_key(cur_user.id, 'sql_beta_access')
    
    if request.method == 'POST':
        secret_code = request.POST.get('secret_code')
        code = Alpha_and_beta_test()
        
        # Try to get the permission status from cache
        is_allowed_user = cache.get(cache_key)
        
        if is_allowed_user is None:
            # If not in cache, check the database
            try:
                is_allowed_user = is_allowed_SQL_beta.objects.get(user=cur_user).Is_allowed
                # Cache the result for future requests (e.g., for 1 hour)
                cache.set(cache_key, is_allowed_user, 3600)
            except is_allowed_SQL_beta.DoesNotExist:
                is_allowed_user = False
                # Cache the negative result as well
                cache.set(cache_key, False, 3600)
        
        if secret_code == code and is_allowed_user:
            request.session['secret_code_validated'] = True
            messages.success(request, 'Welcome to the SQL Generation hub. Please be responsible...')
            return redirect('chat_submit_view')
        else:
            messages.warning(request, 'Your code is incorrect or you are not allowed. Please check and try again.')

    return render(request, 'secretCode.html', {})

# Views to update the user for upcoming features on the specific routes
@login_required(login_url='/login/')
def generate_sql(request):
    cur_user = request.user
    cache_key = get_cache_key(cur_user.id, 'sql_beta_access')
    
    # Try to get the permission status from cache
    is_allowed_user = cache.get(cache_key)
    
    if is_allowed_user is None:
        # If not in cache, check the database
        try:
            is_allowed_user = is_allowed_SQL_beta.objects.get(user=cur_user).Is_allowed
            # Cache the result for future requests (e.g., for 1 hour)
            cache.set(cache_key, is_allowed_user, 3600)
        except is_allowed_SQL_beta.DoesNotExist:
            is_allowed_user = False
            # Cache the negative result as well
            cache.set(cache_key, False, 3600)

    if is_allowed_user and request.session.get('secret_code_validated', False):
        messages.success(request, 'Welcome to the SQL Generation hub. Please be responsible...')
        return redirect('chat_submit_view')
    
    # Show "Coming Soon" message for all users, regardless of their permission status
    messages.info(request, 'This feature is Coming Soon. It will be available in July 2024.')
    return render(request, 'generate_sql.html', {})



# views to handle the management route for database information management
@login_required(login_url='login_user')
def management(request):
    cur_user = request.user
    
    # Check if it's the first time access
    first_time_key = get_cache_key(cur_user.id, 'first_time_management')
    first_time = cache.get(first_time_key) is None

    if first_time:
        # It's the first time, so we'll fetch everything from the database
        dbObj = DatabaseType.objects.all()
        cur_db_type = [db.name for db in dbObj if db.name != 'SQLite']
        databases = list(DatabaseUpload.objects.filter(user=cur_user).select_related('type').order_by('id'))
        
        # Cache the database types
        cache.set(get_cache_key(cur_user.id, 'db_types'), cur_db_type, timeout=3600)
        
        # Cache the databases
        serialized_data = serializers.serialize('json', databases, use_natural_foreign_keys=True)
        cache.set(get_cache_key(cur_user.id, 'databases'), serialized_data, timeout=3600)
        
        # Set the first time flag to False
        cache.set(first_time_key, False, timeout=None)  # No expiration
    else:
        # Not the first time, use cached data
        cur_db_type = cache.get(get_cache_key(cur_user.id, 'db_types'))
        if cur_db_type is None:
            # If cache expired, fetch from database
            dbObj = DatabaseType.objects.all()
            cur_db_type = [db.name for db in dbObj if db.name != 'SQLite']
            cache.set(get_cache_key(cur_user.id, 'db_types'), cur_db_type, timeout=3600)
        
        # Get cached user databases
        databases = get_cached_user_databases(cur_user)

    context = {
        'databases': databases,
        'db_host': cur_db_type,
        'first_time': first_time
    }

    return render(request, 'management.html', context)



@login_required(login_url='login_user')
def database_schema(request, database_id):
    cache_key = get_cache_key(request.user.id, f'schema_{database_id}')
    cached_schema = cache.get(cache_key)

    if cached_schema:
        return render(request, 'database_schema.html', {'schema': cached_schema, 'dbObj': None})

    try:
        database = DatabaseUpload.objects.get(id=database_id)

        if database.user != request.user:
            messages.error(request, "You're not authorized to access this database.")
            return redirect('management')

        db_type = database.type.name
        schema = None

        if db_type == "SQLite":
            if database.hostType == 'cloud':
                try:
                    file_content = download_from_b2(database.b2_file_key)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite') as temp_file:
                        temp_file.write(file_content.getvalue())
                        database_path = temp_file.name
                    schema = get_database_schema(db_type=db_type, database_path=database_path)
                    os.unlink(database_path)
                except Exception as e:
                    messages.error(request, f"Error processing cloud database: {str(e)}")
            else:
                schema = get_database_schema(db_type=db_type, database_path=database.file.path)
        else:
            schema = get_database_schema(db_type=db_type, database_path=database)

        if schema and 'error' not in schema:
            cache.set(cache_key, schema, timeout=300)  # Cache for 5 hour
            return render(request, 'database_schema.html', {'schema': schema, 'dbObj': database})
        else:
            messages.error(request, schema.get('error', 'Unknown error occurred'))
            return render(request, 'database_schema.html', {'schema': {}, 'dbObj': database})

    except DatabaseUpload.DoesNotExist:
        messages.error(request, "Database not found.")
        return redirect('management')
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return render(request, 'database_schema.html', {'schema': None, 'dbObj': None})
    


@login_required(login_url='login_user')
def upload_database(request):
    if request.method == 'POST':
        if 'database_file' in request.FILES or 'database_name' in request.POST:
            try:
                database_file = request.FILES.get('database_file', None)
                database_name = request.POST.get('database_name')
                database_type_id = request.POST.get('database_type')
                hostType = request.POST.get('hostType')
                user = request.user
                database_type = DatabaseType.objects.get(id=database_type_id)

                if database_file:
                    # Upload file to B2 Bucket
                    file_key = f"uploads/{user.id}/{database_name}/{database_file.name}"
                    response = upload_to_b2(database_file, file_key)
                    messages.success(request, response)
                    invalidate_user_databases_cache(request.user)
                    
                    # Get file size
                    b2_client = get_b2_client()
                    obj = b2_client.head_object(Bucket=settings.B2_BUCKET_NAME, Key=file_key)
                    file_size = obj['ContentLength']
                else:
                    file_key = f"uploads/{user.id}/{database_name}/placeholder.txt"
                    file_size = None

                # Create DatabaseUpload record
                database_upload = DatabaseUpload(
                    user=user,
                    name=database_name,
                    b2_file_key=file_key,
                    size=file_size,
                    type=database_type,
                    hostType=hostType
                )
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



def execute_sqlite_query(user, db_path, query):
    # Clean the query from comments
    clean_query = re.sub(r'^\s*--.*\n', '', query, flags=re.MULTILINE).strip()
    
    # Extract the first SQL command to determine query type
    match = re.match(r'^\s*(\w+)', clean_query)
    if match:
        query_type = match.group(1).upper()
    else:
        return "Invalid query format", None, None
    
    # Check user permissions
    allowed_commands = set()
    try:
        permissions = DatabasePermissions.objects.get(user=user)
        if permissions.can_select:
            allowed_commands.add("SELECT")
        if permissions.can_insert:
            allowed_commands.add("INSERT")
        if permissions.can_create:
            allowed_commands.add("CREATE")
        if permissions.can_update:
            allowed_commands.add("UPDATE")
        if permissions.can_delete:
            allowed_commands.add("DELETE")
        if permissions.can_drop:
            allowed_commands.add("DROP")
    except DatabasePermissions.DoesNotExist:
        pass  # User is not in the permissions table; assume full access
    
    if query_type not in allowed_commands:
        return f"User does not have permission to execute {query_type} queries", None, None
    
    # Prepare query type object
    query_type_obj = QueryType(type=query_type, val=clean_query)

    # Execute the query and process the result
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(clean_query)
            query_result = cursor.fetchall()
            column_names = [description[0] for description in cursor.description] if cursor.description else []

            if column_names:
                query_result_with_headers = [
                    dict(zip(column_names, row))
                    for row in query_result
                ]
            else:
                query_result_with_headers = 'No results or columns found'
    except Exception as e:
        return f"Error executing query: {e}", None, None

    # Return the results including query_type_obj
    action = query_type_obj
    return query_result_with_headers, column_names, action




@dataclass
class QueryType:
    type: str
    val: str = None

def execute_postgres_query(user, db_path, query):
    try:
        # query_type = query.strip().split()[0].upper()
        clean_query = re.sub(r'^\s*--.*\n', '', query, flags=re.MULTILINE).strip()
        
        # Extract the first SQL command
        match = re.match(r'^\s*(\w+)', clean_query)
        if match:
            query_type = match.group(1).upper()
        else:
            return "Invalid query format", None, None
        # print(query_type)
    except Exception as e:
        return f"Error has occurred on the cleaning up query: {e}", None, None
    try:
        permissions = DatabasePermissions.objects.get(user=user)
        # User is in the permissions table, so we need to check their permissions
        allowed_commands = []
        if permissions.can_select:
            allowed_commands.append("SELECT")
        if permissions.can_insert:
            allowed_commands.append("INSERT")
        if permissions.can_create:
            allowed_commands.append("CREATE")
        if permissions.can_update:
            allowed_commands.append("UPDATE")
        if permissions.can_delete:
            allowed_commands.append("DELETE")
        if permissions.can_drop:
            allowed_commands.append("DROP")
            
        if query_type not in allowed_commands:
            # print(query_type)
            return f"User does not have permission to execute {query_type} queries", None, None
    except DatabasePermissions.DoesNotExist:
        # User is not in the permissions table, so they can do whatever they need
        pass

    # Find the database object
    database = DatabaseUpload.objects.get(user=user, id=db_path.id)
    # Return a database configuration object based on the given database object
    db_conn = DatabaseConnection.objects.get(database=database)

    try:
        # Connection to host database
        conn = get_PostgreSQL_connection(db_name=db_path)
        cursor = conn.cursor()
        cursor.execute(query)

        query_result_with_headers = None
        column_names = None

        query_type_obj = QueryType(type=query_type, val=query)

        if query_type == "SELECT":
            query_result = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            query_result_with_headers = [
                {column_names[i]: value for i, value in enumerate(row)}
                for row in query_result
            ]
        else:
            conn.commit()
    except Exception as e:
        return Exception(f"Error executing {e}"), None, None
    conn.close()
    return query_result_with_headers, column_names, query_type_obj



def execute_mysql_query(user, db_path, query):
     # Remove initial comments and leading whitespace
    # clean_query = re.sub(r'^\s*--.*\n', '', query, flags=re.MULTILINE).strip()
    
    # # Extract the first SQL command
    # match = re.match(r'^\s*(\w+)', clean_query)
    # if match:
    #     query_type = match.group(1).upper()
    # else:
    #     return "Invalid query format", None, None
    
    # try:
    #     permissions = DatabasePermissions.objects.get(user=user)
    #     # User is in the permissions table, so we need to check their permissions
    #     allowed_commands = []
    #     if permissions.can_select:
    #         allowed_commands.append("SELECT")
    #     if permissions.can_insert:
    #         allowed_commands.append("INSERT")
    #     if permissions.can_create:
    #         allowed_commands.append("CREATE")
    #     if permissions.can_update:
    #         allowed_commands.append("UPDATE")
    #     if permissions.can_delete:
    #         allowed_commands.append("DELETE")
    #     if permissions.can_drop:
    #         allowed_commands.append("DROP")
            
    #     if query_type not in allowed_commands:
    #         # print(query_type)
    #         return f"User does not have permission to execute {query_type} queries", None, None
    # except DatabasePermissions.DoesNotExist:
    #     # User is not in the permissions table, so they can do whatever they need
    #     pass 
    
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
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        query_result = cursor.fetchall()
        column_names = cursor.column_names
        query_result_with_headers = [
            {column_names[i]: value for i, value in enumerate(row)}
            for row in query_result
        ]
        conn.close()
    except Exception as e:
        return Exception(f"Error executing {e}"), None, None
    return query_result_with_headers, column_names, None



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
         # check if the demo user is trying to update the connection 
        if request.user.username == 'TestUser':
            messages.error(request, 'You are not authorized to update the connection for this database because it is a demo database.')
            return redirect(db_connection, id=id)
        
        
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
    # hide the connection for the demo User from the public 
    if request.user.username == 'TestUser':
        previewConn = {
            'host': '*' * 25, 
            'port': 9999,  # Keep the port number as is
            'dbname': '*' * 15, 
            'user': '*' * 15, 
            'password': '*' * 45
        }


    return render(request, 'database-connections.html', {'dbObject': dbObject, 'previewConn': previewConn})





# def games(request):
#     context = {}
#     if request.method == 'POST':
#         user_answer = request.POST.get('user_answer')
#         previous_question = request.POST.get('previous_question')
#         user_performance = request.POST.get('user_performance') == 'True'

#         # Check if previous_question is empty or None, indicating the start of the game
#         if not previous_question:
#             # Start with an easy question
#             initial_question, initial_difficulty = get_next_sql_question('', '', True)
#             context.update({'next_question': initial_question, 'difficulty': initial_difficulty})
#         else:
#             # Continue with the next question based on user's performance
#             response = get_next_sql_question(previous_question, user_answer, user_performance, request.user.username)
#             context.update({'next_question': response[0], 'difficulty': response[1]})
#         context = get_next_sql_question(user_answer)
#         return render(request, 'games.html', context)
#     else:
#         # Initial welcome message
#         context.update({'welcome_message': f"{request.user.username}, welcome! Do you want to play the SQL game?"})

#     return render(request, 'games.html', context)


# def devAi(request):
#     answer = ''
#     if request.method == 'POST':
#         question = request.POST.get('question')
#         answer = code_generator(question)
#     return render(request, 'devAi.html', {'answer': answer})
    




if __name__ == '__main__':
    debug = True

