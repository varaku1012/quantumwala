# Authentication System Design

## Architecture
- REST API with JWT authentication
- Stateless authentication
- Redis session cache
- PostgreSQL user store

## Endpoints
- POST /auth/register
- POST /auth/login
- POST /auth/logout
- POST /auth/refresh
- POST /auth/reset-password
- POST /auth/verify-email
- POST /auth/mfa/enable
- POST /auth/mfa/verify
