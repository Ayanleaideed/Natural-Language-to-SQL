import os
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

# Configure the Gemini API with your API key
genai.configure(api_key=api_key)

def generate_sql_query(natural_language_query, databases_context):
    prompt_template = os.getenv('PROMPT_TEMPLATE')
    sql_type = 'sqlite'
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

def get_database_schema(database_path):
    """
    Queries the SQLite database and returns the schema information including all tables and their columns.

    :param database_path: Path to the SQLite database file.
    :return: A dictionary containing table names as keys and a list of column definitions as values.
    """
    schema = {}
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Query to get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            schema[table_name] = [{"name": column[1], "type": column[2]} for column in columns]
        
        # Close the connection
        conn.close()
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return None
    
    return schema


def get_sql_question_answer(question, context_data):
    prompt_sql_generator =  os.getenv("PROMPT_SQL_GENERATOR")
    prompt_sql_generator = prompt_sql_generator.format(question=question, context_data=context_data)
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
