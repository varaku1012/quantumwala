# EtsyPro AI Authentication Service

A secure, scalable authentication microservice for the EtsyPro AI platform, featuring OAuth2 integration with Etsy, multi-factor authentication, and enterprise-grade security.

## Features

- **Secure Authentication**: JWT-based authentication with RS256 signing
- **Etsy OAuth2 Integration**: Seamless connection with Etsy shops
- **Multi-Factor Authentication**: Support for TOTP, SMS, and email-based 2FA
- **Password Security**: Bcrypt hashing with factor 12, password complexity requirements
- **Session Management**: Redis-based session storage with device tracking
- **Role-Based Access Control**: Flexible permission system for teams
- **Security Features**: Rate limiting, CSRF protection, SQL injection prevention
- **Email Integration**: SendGrid for transactional emails
- **SMS Integration**: Twilio for SMS-based 2FA
- **Health Monitoring**: Comprehensive health check endpoints

## Tech Stack

- **Runtime**: Node.js 20+
- **Framework**: NestJS
- **Language**: TypeScript
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Email**: SendGrid
- **SMS**: Twilio
- **Container**: Docker
- **Orchestration**: Kubernetes

## Getting Started

### Prerequisites

- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)
- Etsy API credentials
- SendGrid API key
- Twilio account (for SMS 2FA)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/etsypro/auth-service.git
cd auth-service
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment variables:
```bash
cp .env.example .env
```

4. Update `.env` with your configuration:
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=your-password
DB_NAME=etsypro_auth

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET=your-jwt-secret
JWT_REFRESH_SECRET=your-refresh-secret

# Etsy OAuth
ETSY_CLIENT_ID=your-etsy-client-id
ETSY_CLIENT_SECRET=your-etsy-client-secret

# SendGrid
SENDGRID_API_KEY=your-sendgrid-key

# Twilio (optional)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

5. Run database migrations:
```bash
npm run migration:run
```

6. Start the service:
```bash
npm run dev
```

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. The service will be available at `http://localhost:3001`

## API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd123"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd123",
  "rememberMe": true
}
```

#### OAuth with Etsy
```http
GET /api/v1/auth/etsy?redirect_uri=https://app.example.com/callback
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refreshToken": "your-refresh-token"
}
```

### MFA Endpoints

#### Enable MFA
```http
POST /api/v1/auth/mfa/enable
Authorization: Bearer your-jwt-token
Content-Type: application/json

{
  "type": "totp" // or "sms", "email"
}
```

#### Verify MFA
```http
POST /api/v1/auth/mfa/verify
Authorization: Bearer your-jwt-token
Content-Type: application/json

{
  "code": "123456",
  "type": "totp"
}
```

## Security

### Password Requirements
- Minimum 12 characters
- Must contain uppercase, lowercase, number, and special character
- Cannot be in common password list
- Different from last 5 passwords

### Rate Limiting
- Default: 100 requests per minute per IP
- Configurable via environment variables

### Session Security
- Sessions expire after 30 days (remember me) or 24 hours
- Device fingerprinting for anomaly detection
- Automatic session cleanup for expired sessions

### MFA Options
1. **TOTP**: Compatible with Google Authenticator, Authy, etc.
2. **SMS**: 6-digit codes via Twilio
3. **Email**: 6-digit codes via SendGrid

## Testing

### Run Tests
```bash
# Unit tests
npm run test

# Unit tests with coverage
npm run test:cov

# E2E tests
npm run test:e2e

# Security tests
npm run test:security
```

### Test Coverage Goals
- Unit tests: 90%+
- Integration tests: All endpoints
- Security tests: OWASP Top 10
- Performance tests: 10K concurrent users

## Deployment

### Kubernetes

1. Create namespace:
```bash
kubectl create namespace etsypro
```

2. Apply secrets:
```bash
kubectl apply -f k8s/secrets.yaml
```

3. Deploy:
```bash
kubectl apply -f k8s/
```

### Environment Variables

See `.env.example` for all available configuration options.

### Health Checks

- **Liveness**: `/api/v1/health/live`
- **Readiness**: `/api/v1/health/ready`
- **Full Health**: `/api/v1/health`

## Monitoring

### Metrics
- Authentication success/failure rates
- Token generation time
- Session count by user
- MFA adoption rate
- Failed login attempts

### Alerts
- High error rate (>5%)
- Slow response times (>500ms)
- Database connection failures
- Redis connection failures
- Unusual login patterns

## Development

### Project Structure
```
src/
├── api/              # Controllers and DTOs
├── auth/             # Authentication logic
├── cache/            # Redis integration
├── core/             # Entities and repositories
├── email/            # Email service
├── health/           # Health checks
├── mfa/              # Multi-factor auth
├── oauth/            # OAuth integration
├── sessions/         # Session management
└── users/            # User management
```

### Code Style
- ESLint configuration included
- Prettier for formatting
- Pre-commit hooks with Husky

### Contributing
1. Fork the repository
2. Create feature branch
3. Write tests
4. Submit pull request

## License

Proprietary - EtsyPro AI

## Support

For issues and questions:
- Email: support@etsypro.ai
- Documentation: https://docs.etsypro.ai
- Status: https://status.etsypro.ai