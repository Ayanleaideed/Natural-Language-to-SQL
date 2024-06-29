import os
import sqlite3

import google.generativeai as genai
import mysql.connector
import psycopg2
from dotenv import load_dotenv
from mysql.connector import Error

from .models import DatabaseConnection

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

# Configure the Gemini API with your API key
genai.configure(api_key=api_key)

def generate_sql_query(dbType, natural_language_query, databases_context):
    prompt_template = os.getenv('PROMPT_TEMPLATE')
    sql_type = dbType
   # Format the prompt with actual values
    prompt = prompt_template.format(Sql_type=sql_type, natural_language_query=natural_language_query, databases_context=databases_context)

    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        # Generate the SQL query from the natural language query
        response = model.generate_content(prompt)

        # Extract and clean up the SQL query
        sql_query = response.text.strip()
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()

        return sql_query
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None

def get_database_schema(db_type, database_path):
    schema = {}
    try:
        if db_type == "SQLite":
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                schema[table_name] = [{"name": column[1], "type": column[2]} for column in columns]
            conn.close()
        elif db_type == "PostgreSQL":
            conn = get_PostgreSQL_connection(database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
                columns = cursor.fetchall()
                schema[table_name] = [{"name": column[0], "type": column[1]} for column in columns]
            conn.close()
        elif db_type == "MySQL":
          conn = get_mysql_connection(database_path)
          cursor = conn.cursor()
          cursor.execute("SHOW TABLES;")
          tables = cursor.fetchall()
          for table in tables:
              table_name = table[0]
              cursor.execute(f"DESCRIBE {table_name};")
              columns = cursor.fetchall()
              schema[table_name] = [{"name": column[0], "type": column[1]} for column in columns]
          conn.close()


        else:
            error = f"Unsupported database type: {db_type}"
            return error
    except sqlite3.DatabaseError as e:
        error = f"SQLite database error: {e}"
        return error
    except psycopg2.DatabaseError as e:
        error = f"PostgreSQL database error: {e}"
        return error
    except mysql.connector.Error as e:
        error = f"MySQL database error: {e}"

    return schema


# method to connect given database name
def get_PostgreSQL_connection(db_name):
    try:
        db_conn = DatabaseConnection.objects.get(database=db_name)
        conn = psycopg2.connect(
            dbname=db_conn.dbname,
            user= db_conn.user,
            password=db_conn.password,
            host=db_conn.host,
            port=db_conn.port
        )
        return conn
    except DatabaseConnection.DoesNotExist:
        return f"Database connection with name '{db_name}' does not exist."
    except psycopg2.Error as e:
        return f"Error connecting to database '{db_name}': {e}"


def get_mysql_connection(db_name):
    try:
        db_conn = DatabaseConnection.objects.get(database=db_name)
        conn = mysql.connector.connect(
            host=db_conn.host,
            user=db_conn.user,
            password=db_conn.password,
            database=db_conn.dbname,
            port=db_conn.port
        )
        return conn
    except DatabaseConnection.DoesNotExist:
        return f"Database connection with name '{db_name}' does not exist."
    except Error as e:
        return f"Error connecting to database '{db_name}': {e}"


def get_sql_question_answer(question):
    prompt_sql_generator =  os.getenv("PROMPT_SQL_GENERATOR")
    prompt_sql_generator = prompt_sql_generator.format(question=question)
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        # Generate the SQL query from the natural language query
        response = model.generate_content(prompt_sql_generator)

        # Extract and clean up the SQL query
        sql_query = response.text.strip()
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()

        return sql_query
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None



def Alpha_and_beta_test():
    secret_code = os.getenv('SECRET_CODE')
    if secret_code:
        return secret_code
    else:
        return None


from datetime import datetime, timedelta


def get_time(seconds):
    # Calculate adjusted time
    current_time = datetime.now()
    wait_time = timedelta(seconds=seconds)
    adjusted_time = current_time + wait_time
    formatted_adjusted_time = adjusted_time.strftime("%I:%M %p")

    return formatted_adjusted_time




def get_next_sql_question(previous_question, user_answer, user_performance, username=None):
    # Define the prompt template
    prompt_template_sql_games = os.getenv('prompt_template_sql_games')

    # Determine the next difficulty level
    easy_questions = ["Write an SQL query to find the employees who earn more than $50,000 per year."]
    medium_questions = ["Write an SQL query to find the average salary of employees in each department."]
    hard_questions = ["Write an SQL query to find the employees who have been with the company for more than 5 years and earn more than $50,000 per year."]

    if user_performance:
        if previous_question in easy_questions:
            difficulty = "medium"
        elif previous_question in medium_questions:
            difficulty = "hard"
        else:
            difficulty = "hard"
        performance = "correctly"
    else:
        if previous_question in hard_questions:
            difficulty = "medium"
        elif previous_question in medium_questions:
            difficulty = "easy"
        else:
            difficulty = "easy"
        performance = "incorrectly"

    # Fill in the prompt template
    prompt = prompt_template_sql_games.format(
        username=username,
        performance=performance,
        difficulty=difficulty,
        previous_question=previous_question,
        user_answer=user_answer
    )

    # Use the GenerativeModel to generate the next question
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content(prompt)

    next_question = response.text.strip()
    return next_question, difficulty

