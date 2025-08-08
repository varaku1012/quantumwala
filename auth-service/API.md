# API Documentation

## Authentication Service API v1.0

### Base URL
```
http://localhost:3000
```

### Authentication
Protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

### Error Responses
All endpoints return errors in the following format:
```json
{
  "error": "Error message"
}
```

### Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

### Rate Limiting
- 100 requests per minute per IP
- 10 failed login attempts per hour per email

### Versioning
API version is included in the URL: `/v1/auth/...`
