# Authentication Service

## Overview
A complete authentication service with JWT tokens, MFA support, and password reset functionality.

## Features
- User registration with email verification
- JWT-based authentication
- Multi-factor authentication (TOTP)
- Password reset via email
- Session management
- Role-based access control

## Installation

```bash
npm install
```

## Configuration

Create a `.env` file based on `.env.example`:

```
PORT=3000
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/authdb
```

## Running the Service

### Development
```bash
npm run dev
```

### Production
```bash
npm start
```

### Testing
```bash
npm test
```

## API Endpoints

### Public Endpoints

#### POST /auth/register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "emailVerified": false
  }
}
```

#### POST /auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "jwt-token",
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  }
}
```

#### POST /auth/forgot-password
Request password reset.

**Request:**
```json
{
  "email": "user@example.com"
}
```

#### POST /auth/reset-password
Reset password with token.

**Request:**
```json
{
  "token": "reset-token",
  "newPassword": "NewSecurePassword123!"
}
```

### Protected Endpoints

#### GET /auth/mfa/setup
Get MFA setup QR code.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "secret": "base32-secret",
  "qrCode": "data:image/png;base64,..."
}
```

#### POST /auth/mfa/verify
Verify MFA token.

**Request:**
```json
{
  "token": "123456",
  "secret": "base32-secret"
}
```

## Database Schema

### Users Table
- id: UUID (Primary Key)
- email: VARCHAR(255) (Unique)
- password_hash: VARCHAR(255)
- email_verified: BOOLEAN
- mfa_enabled: BOOLEAN
- mfa_secret: VARCHAR(255)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

### Sessions Table
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key)
- token: VARCHAR(500)
- refresh_token: VARCHAR(500)
- expires_at: TIMESTAMP
- created_at: TIMESTAMP

## Security Considerations
- Passwords are hashed using bcrypt
- JWT tokens expire after 24 hours
- MFA uses TOTP (Time-based One-Time Password)
- Password reset tokens expire after 1 hour
- All sensitive endpoints require authentication

## Testing
Run tests with coverage:
```bash
npm test -- --coverage
```

## License
MIT
