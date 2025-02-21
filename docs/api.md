# API Documentation

## REST API Endpoints

### Convert Natural Language to SQL

```http
POST /api/convert
Content-Type: application/json

{
    "query": "Show me all users from New York",
    "schema": "users"
}
```

### Response

```json
{
  "sql": "SELECT * FROM users WHERE location = 'New York'",
  "params": {},
  "metadata": {
    "confidence": 0.95,
    "tables": ["users"]
  }
}
```

## WebSocket API

### Real-time Query Building

```javascript
ws.connect("/ws/query-builder");
```

## Error Codes

- `400` - Invalid input
- `401` - Unauthorized
- `403` - Forbidden
- `500` - Server error

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per day per API key

## Authentication

Bearer token authentication:

```http
Authorization: Bearer <your_api_key>
```

## Examples

### Complex Queries

```http
POST /api/convert
{
    "query": "Find average salary of employees in IT department hired after 2020",
    "schema": "employees"
}
```

### Response

```json
{
  "sql": "SELECT AVG(salary) FROM employees WHERE department = 'IT' AND hire_date > '2020-01-01'",
  "metadata": {
    "tables": ["employees"],
    "columns": ["salary", "department", "hire_date"]
  }
}
```
