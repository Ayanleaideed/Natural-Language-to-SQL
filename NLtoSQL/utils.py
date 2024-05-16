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
    """
    Generates an SQL query from a natural language query using Google Gemini API.
    
    :param natural_language_query: The natural language query to be converted.
    :param databases_context: The context of the database schema.
    :return: A valid SQL query as a string.
    """
    prompt = f"""
    The user will provide a natural language request, and you need to return a corresponding SQL query for an SQLite database. 
    The response should be a valid SQL query and not a natural language explanation. 
    Example input: "Give me all the movies in the database." 
    Example output: "SELECT * FROM movies;"
    Here is the database schema: {databases_context}

    Natural language query: {natural_language_query}
    """
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

# Example usage
if __name__ == "__main__":
    database_path = "path/to/your/database.db"
    natural_language_query = "Give me all the movies in the database."

    schema = get_database_schema(database_path)
    if schema:
        databases_context = "\n".join([f"Table {table}: {columns}" for table, columns in schema.items()])
        sql_query = generate_sql_query(natural_language_query, databases_context)
        if sql_query:
            print(f"Generated SQL Query: {sql_query}")
        else:
            print("Failed to generate SQL query.")
    else:
        print("Failed to retrieve database schema.")




# SELECT * FROM MOVIES LIMIT 20

# Can you get me 10 movies and the stars of that movie rating of that movie the title that movie on the actors of that movie