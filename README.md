# QueryCraft: Database Management & NL Query Engine

<div align="center">

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)

</div>

## Project Overview

QueryCraft is a full-stack database management system that goes beyond basic NL-to-SQL conversion. While it includes natural language query capabilities, its core strength lies in its robust database management features, schema analysis, and multi-database orchestration.

### Core Technical Features

#### Database Engine Integration

- Custom connection pooling for PostgreSQL, MySQL, and SQLite
- Dynamic schema introspection and mapping
- Query execution engine with cross-database compatibility
- B2 cloud storage integration for database file management

#### Query Processing Pipeline

- Context-aware query parsing with database schema validation
- Query templating and parameterization
- Real-time query execution monitoring
- Query optimization through execution plan analysis

#### Security Implementation

- Granular permission matrix for database operations
- Query sanitization and validation pipeline
- Rate limiting with Redis-backed request tracking
- Session-based authentication with custom middleware

## Technical Architecture

### Data Model

```mermaid
erDiagram
    DatabaseUpload ||--|| DatabaseConnection : manages
    DatabaseUpload ||--o{ QueryHistory : tracks
    User ||--|| DatabasePermissions : has
    QueryHistory ||--o{ APIUsage : monitors

    DatabaseUpload {
        string name
        string hostType
        string b2_file_key
        datetime uploaded_at
    }

    DatabaseConnection {
        string host
        int port
        string dbname
        encrypted password
    }

    DatabasePermissions {
        boolean can_select
        boolean can_insert
        boolean can_update
        boolean can_delete
    }
```

### Implementation Details

#### Backend Components

```python
# Query Execution Pipeline
def execute_query(db_type, user, database, query):
    if db_type == 'SQLite':
        return execute_sqlite_query(user, database.file.path, query)
    elif db_type == 'PostgreSQL':
        return execute_postgres_query(user, database, query)
    elif db_type == 'MySQL':
        return execute_mysql_query(user, database, query)
```

#### Database Connection Management

```python
# Dynamic Database Connection Pool
class DatabaseConnection(models.Model):
    database = models.ForeignKey(DatabaseUpload, on_delete=models.CASCADE)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    dbname = models.CharField(max_length=255)
    connection_date = models.DateTimeField(auto_now_add=True)
```

#### Rate Limiting Implementation

```python
@classmethod
def check_rate_limit(cls, user, endpoint, max_requests, period):
    now = timezone.now()
    period_ago = now - timezone.timedelta(seconds=period)
    requests = cls.objects.filter(
        user=user,
        endpoint=endpoint,
        timestamp__gte=period_ago
    )
    return requests.count() < max_requests
```

## Deployment & Setup

### Environment Configuration

```bash
# Core settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECRET_KEY=your-secret-key

# Database URLs
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0

# Storage Configuration
B2_BUCKET_NAME=your-bucket
B2_APP_KEY=your-app-key
B2_APP_KEY_ID=your-key-id
```

### Database Migration

```bash
# Initialize database schema
python manage.py makemigrations
python manage.py migrate

# Set up initial permissions
python manage.py setup_permissions
```

## API Reference

### Database Operations

```http
POST /api/databases/upload/
Content-Type: multipart/form-data

{
    "file": binary,
    "name": "database_name",
    "type": "sqlite|postgresql|mysql"
}
```

```http
POST /api/query/
Content-Type: application/json

{
    "database_id": 1,
    "query": "SELECT * FROM users WHERE active = true",
    "params": {}
}
```

### Schema Management

```http
GET /api/databases/{id}/schema/
Authorization: Bearer <token>

Response: {
    "tables": [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "integer", "constraints": ["PRIMARY KEY"]},
                {"name": "email", "type": "varchar", "constraints": ["UNIQUE"]}
            ],
            "indexes": ["email_idx"]
        }
    ]
}
```

## Development

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run test suite with coverage
pytest --cov=. tests/

# Run specific test categories
pytest tests/test_query_execution.py
pytest tests/test_permissions.py
```

## License

MIT License - see LICENSE for details.

---

<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ayanle-aideed-118752252/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Ayanleaideed)

</div>
