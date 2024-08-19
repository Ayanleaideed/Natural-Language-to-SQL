import os
import sqlite3
import re
import mysql.connector
import psycopg2
from dotenv import load_dotenv
from mysql.connector import Error
from .models import DatabaseConnection
from django.conf import settings
import requests
import io
import tempfile
from datetime import datetime, timedelta
import google.generativeai as genai



# Load environment variables from .env file
load_dotenv()

# Retrieve the Google API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

# Configure the Generative AI API with your API key
genai.configure(api_key=api_key)

# Function to generate SQL query from natural language query using Generative AI
def generate_sql_query(dbType, natural_language_query, databases_context):
    prompt_template = os.getenv('PROMPT_TEMPLATE')
    sql_type = dbType
    # Format the prompt with actual values
    prompt = prompt_template.format(Sql_type=sql_type, natural_language_query=natural_language_query, databases_context=databases_context)

    try:
        # Initialize the Generative AI model
        # model = genai.GenerativeModel('gemini-1.5-pro-latest')
        model = genai.GenerativeModel('gemini-1.5-flash')


        # Generate the SQL query from the natural language query
        response = model.generate_content(prompt)

        # Extract and clean up the SQL query
        sql_query = response.text.strip()
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()

        return sql_query
    except Exception as e:
        # return e
        return  Exception('Error has occurred while generating: %s' % e)

    
    # Function to get the database schema based on the database type
def get_database_schema(db_type, database_path):
    schema = {}
    try:
        if db_type == "SQLite":
            # print(f"Debug: Connecting to SQLite database at path: {database_path}")
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # Get tables and their columns
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                # Get foreign key information
                cursor.execute(f"PRAGMA foreign_key_list({table_name});")
                foreign_keys = cursor.fetchall()
                # Build schema for each table
                schema[table_name] = {
                    "columns": [],
                    "foreign_keys": []
                }
                for column in columns:
                    col_info = {
                        "name": column[1],
                        "type": column[2],
                        "constraints": []
                    }
                    if column[3]:  # NOT NULL
                        col_info["constraints"].append("NOT NULL")
                    if column[5]:  # PRIMARY KEY
                        col_info["constraints"].append("PRIMARY KEY")
                    schema[table_name]["columns"].append(col_info)
                for fk in foreign_keys:
                    schema[table_name]["foreign_keys"].append({
                        "from": fk[3],
                        "to": f"{fk[2]}.{fk[4]}"
                    })
            conn.close()

        elif db_type == "PostgreSQL":
            # Connect to PostgreSQL database
            conn = get_PostgreSQL_connection(database_path)
            cursor = conn.cursor()

            # Get tables and their columns
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
                columns = cursor.fetchall()

                # Get foreign key information
                cursor.execute(f"""
                    SELECT
                        tc.constraint_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM
                        information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE
                        tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='{table_name}';
                """)
                foreign_keys = cursor.fetchall()

                # Build schema for each table
                schema[table_name] = {
                    "columns": [],
                    "foreign_keys": []
                }

                for column in columns:
                    col_info = {
                        "name": column[0],
                        "type": column[1],
                        "constraints": []  # Placeholder for constraints (to be added)
                    }

                    # Fetch constraints for each column
                    cursor.execute(f"""
                        SELECT
                            tc.constraint_type
                        FROM
                            information_schema.table_constraints AS tc
                            JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                        WHERE
                            kcu.table_name = '{table_name}' AND kcu.column_name = '{column[0]}';
                    """)
                    constraints = cursor.fetchall()
                    col_info["constraints"] = [constraint[0] for constraint in constraints]

                    schema[table_name]["columns"].append(col_info)

                for fk in foreign_keys:
                    schema[table_name]["foreign_keys"].append({
                        "constraint_name": fk[0],
                        "from_column": fk[1],
                        "to_table": fk[2],
                        "to_column": fk[3]
                    })

            conn.close()


        elif db_type == "MySQL":
            # Connect to MySQL database
            conn = get_mysql_connection(database_path)
            cursor = conn.cursor()

            # Get tables and their columns
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DESCRIBE {table_name};")
                columns = cursor.fetchall()

                # Get foreign key information
                cursor.execute(f"SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_NAME = '{table_name}';")
                foreign_keys = cursor.fetchall()

                # Build schema for each table
                schema[table_name] = {
                    "columns": [],
                    "foreign_keys": []
                }

                for column in columns:
                    col_info = {
                        "name": column[0],
                        "type": column[1],
                        "constraints": []  # Placeholder for constraints (to be added)
                    }
                    # Add additional code here to fetch constraints for MySQL
                    schema[table_name]["columns"].append(col_info)

                for fk in foreign_keys:
                    schema[table_name]["foreign_keys"].append({
                        "from": fk[1],  # TODO: Adjust based on MySQL foreign key query result
                        "to": f"{fk[2]}.{fk[3]}"  #TODO Adjust based on MySQL foreign key query result
                    })

            conn.close()

        else:
            error = f"Unsupported database type: {db_type}"
            return {"error": error}

    except sqlite3.DatabaseError as e:
        error = f"SQLite database error: {e}"
        return {"error": error}

    except psycopg2.DatabaseError as e:
        error = f"PostgreSQL database error: {e}"
        return {"error": error}

    except mysql.connector.Error as e:
        error = f"MySQL database error: {e}"
        return {"error": error}

    except AttributeError as e:
        if "'str' object has no attribute 'cursor'" in str(e):
            # TODO: handle or show the database if locally hosted they need to run the server for the database connection
            # if data
            error = "The database connection is invalid. Please make sure to update your connection settings."
        else:
            error = f"An unexpected error occurred: {e}"
        return {"error": error}

    except Exception as e:
        error = f"An unexpected error occurred: {e}"
        return {"error": error}

    return schema


# Function to establish connection with PostgreSQL database
def get_PostgreSQL_connection(db_name):
    try:
        db_conn = DatabaseConnection.objects.get(database=db_name)
        conn = psycopg2.connect(
            dbname=db_conn.dbname,
            user=db_conn.user,
            password=db_conn.password,
            host=db_conn.host,
            port=db_conn.port
        )
        return conn

    except DatabaseConnection.DoesNotExist:
        return f"Database connection with name '{db_name}' does not exist."

    except psycopg2.Error as e:
        return f"Error connecting to database '{db_name}': {e}"

# Function to establish connection with MySQL database
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



# Function to generate SQL query from natural language question
def get_sql_question_answer(question):
    prompt_sql_generator = os.getenv("PROMPT_SQL_GENERATOR")
    if prompt_sql_generator is None:
        return ValueError("PROMPT_SQL_GENERATOR environment variable is not set.")
    
    prompt_sql_generator = prompt_sql_generator.format(question=question)
    
    try:
        # Initialize the Generative AI model
        # model = genai.GenerativeModel('gemini-1.5-pro-latest')
        model = genai.GenerativeModel('gemini-1.5-flash')


        # Generate the SQL query from the natural language question
        response = model.generate_content(prompt_sql_generator)

        # Extract and clean up the SQL query
        sql_query = response.text.strip()
        sql_query = re.sub(r'\*\*', '', sql_query)
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()

        return sql_query

    except Exception as e:
        return f'Error has occurred while generating: {e}'


# Function to get the next SQL question based on user's performance
def get_next_sql_question(previous_question, user_answer, user_performance, username=None):
    # Define the prompt template for SQL games
    prompt_template_sql_games = os.getenv('prompt_template_sql_games')

    # Define different difficulty levels of SQL questions
    easy_questions = ["Write an SQL query to find the employees who earn more than $50,000 per year."]
    medium_questions = ["Write an SQL query to find the average salary of employees in each department."]
    hard_questions = ["Write an SQL query to find the employees who have been with the company for more than 5 years and earn more than $50,000 per year."]

    # Determine the next difficulty level based on user's performance
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

    # Fill in the prompt template with actual values
    prompt = prompt_template_sql_games.format(
        username=username,
        performance=performance,
        difficulty=difficulty,
        previous_question=previous_question,
        user_answer=user_answer
    )

    # Use the Generative AI model to generate the next question
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content(prompt)

    next_question = response.text.strip()
    return next_question, difficulty


# test feature access for testing users
def Alpha_and_beta_test():
    # secret_code = os.getenv('SECRET_CODE')
    secret_code = settings.SECRET_CODE
    if secret_code:
        return secret_code
    else:
        return None



# Function to transform query result into a structured format
def transform_query_result(query_result, column_names):
    # print('Transforming query result', query_result, 'column names', column_names)
    transformed_result = []
    for row in query_result:
        transformed_row = {column_name: row.get(column_name, None) for column_name in column_names}
        transformed_result.append(transformed_row)
    return transformed_result

# Function to get current time adjusted by seconds
def get_time(seconds):
    current_time = datetime.now()
    wait_time = timedelta(seconds=seconds)
    adjusted_time = current_time + wait_time
    formatted_adjusted_time = adjusted_time.strftime("%I:%M %p")
    return formatted_adjusted_time

import google.generativeai as genai

def code_generator(question):
    try:
        # Automatically create a prompt for a world-class CSS and HTML agent
        prompt = f"""
            You are a world-class CSS and HTML expert. Your goal is to provide the most visually appealing and technically sound code possible, based on the user's input.

            User Input: {question}

            Requirements:
            - Visually Exceptional: Strive for a layout that is both beautiful and highly effective in conveying the information.
            - Technical Excellence: Follow best practices for clean, maintainable code.
            - Talman CSS Color Palette: Incorporate this palette for a cohesive and aesthetically pleasing color scheme.
            - Adaptability: Your code should be flexible enough to handle different content lengths and user preferences.

            Output:
            Provide the complete HTML and CSS code, clearly formatted and well-commented.

            Example:
            If the user input is "Create a webpage showcasing a company's product, including images and a product description," your code should generate a beautiful, responsive webpage incorporating the Talman CSS Color Palette and adhering to all other requirements.
        """

        # Use Google Gemini's newest API or model to generate the code
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Code generation failed. Please try again. Error: {str(e)}"

    
    