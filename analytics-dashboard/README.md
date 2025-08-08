# EtsyPro AI Analytics Dashboard

A comprehensive real-time analytics platform for Etsy sellers, providing predictive insights, competitive intelligence, and customizable dashboards.

## 🚀 Features

### Real-time Analytics
- Live sales tracking with 30-second refresh
- Conversion rate monitoring by product
- Customer engagement analytics
- Real-time dashboard updates via WebSocket

### Predictive Analytics
- AI-powered revenue forecasting (30/60/90 days)
- Demand prediction for inventory optimization
- Price optimization recommendations
- Trend detection and alerts

### Competitive Intelligence
- Market positioning analysis
- Competitor pricing comparison
- Opportunity gap identification
- Trend strength indicators

### Customizable Dashboards
- Drag-and-drop widget system
- 20+ pre-built widget types
- Custom dashboard layouts
- Team sharing capabilities

## 🏗️ Architecture

### Microservices Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   React     │    │  Analytics  │    │     ML      │
│  Frontend   │◄──►│   API       │◄──►│  Service    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │            ┌─────────────┐           │
       └───────────►│  Dashboard  │◄──────────┘
                    │     API     │
                    └─────────────┘
                           │
                    ┌─────────────┐
                    │   Kafka     │
                    │  Streams    │
                    └─────────────┘
                           │
              ┌─────────────┬─────────────┐
              │             │             │
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │TimescaleDB  │ │ PostgreSQL  │ │    Redis    │
       │             │ │             │ │   Cache     │
       └─────────────┘ └─────────────┘ └─────────────┘
```

### Tech Stack
- **Frontend**: React 18 + TypeScript + Redux Toolkit
- **Backend**: Node.js + NestJS + TypeScript
- **ML Service**: Python + FastAPI + TensorFlow
- **Databases**: TimescaleDB + PostgreSQL + Redis
- **Streaming**: Apache Kafka + Kafka Streams
- **Deployment**: Docker + Kubernetes
- **Monitoring**: Prometheus + Grafana

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 6+
- Apache Kafka 3.0+

### Installation

1. **Clone and install dependencies**
```bash
git clone https://github.com/etsypro/analytics-dashboard
cd analytics-dashboard
npm run setup
```

2. **Start infrastructure services**
```bash
# Start databases and Kafka
docker-compose -f infrastructure/docker-compose.yml up -d

# Run database migrations
npm run migrate

# Seed with sample data
npm run seed
```

3. **Start development servers**
```bash
# Start all services
npm run dev

# Or start individually
npm run dev:backend   # Backend API on :3000
npm run dev:frontend  # Frontend on :3001
npm run dev:ml       # ML service on :8001
```

4. **Access the dashboard**
```
http://localhost:3001
```

## 📁 Project Structure

```
analytics-dashboard/
├── backend/                    # NestJS Analytics & Dashboard APIs
│   ├── src/
│   │   ├── analytics/         # Analytics service
│   │   ├── dashboard/         # Dashboard configuration
│   │   ├── auth/             # Authentication
│   │   ├── websocket/        # Real-time updates
│   │   └── common/           # Shared utilities
│   ├── test/
│   └── package.json
├── frontend/                   # React Dashboard Application
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── widgets/          # Dashboard widgets
│   │   ├── pages/           # Application pages
│   │   ├── services/        # API services
│   │   ├── store/           # Redux store
│   │   └── utils/           # Utilities
│   ├── public/
│   └── package.json
├── ml-service/                 # Python ML Inference Service
│   ├── models/               # ML model implementations
│   ├── features/             # Feature engineering
│   ├── api/                  # FastAPI endpoints
│   ├── tests/
│   └── requirements.txt
├── shared/                     # Shared types and utilities
│   ├── types/                # TypeScript types
│   ├── constants/            # Shared constants
│   └── utils/                # Shared utilities
├── infrastructure/             # Infrastructure as Code
│   ├── docker-compose.yml    # Local development
│   ├── k8s/                  # Kubernetes manifests
│   └── terraform/            # Terraform configs
├── e2e-tests/                 # End-to-end tests
├── docs/                      # Documentation
└── scripts/                   # Build and deployment scripts
```

## 🔧 Development

### Environment Variables

Create `.env` files in each service directory:

**Backend (.env)**
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/analytics
TIMESCALE_URL=postgresql://user:pass@localhost:5432/timescale
REDIS_URL=redis://localhost:6379

# Kafka
KAFKA_BROKERS=localhost:9092
KAFKA_CLIENT_ID=analytics-dashboard

# Authentication
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=8h

# External APIs
ETSY_API_KEY=your-etsy-api-key
ETSY_API_SECRET=your-etsy-api-secret

# Monitoring
PROMETHEUS_ENABLED=true
SENTRY_DSN=your-sentry-dsn
```

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:3000
REACT_APP_WS_URL=ws://localhost:3000
REACT_APP_ML_API_URL=http://localhost:8001
REACT_APP_ENVIRONMENT=development
```

**ML Service (.env)**
```env
MODEL_STORAGE_PATH=./models
FEATURE_STORE_URL=postgresql://user:pass@localhost:5432/features
REDIS_URL=redis://localhost:6379
PROMETHEUS_METRICS_PORT=8002
```

### Database Setup

```bash
# Create databases
createdb analytics
createdb timescale
createdb features

# Install TimescaleDB extension
psql -d timescale -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"

# Run migrations
cd backend && npm run migrate

# Create hypertables
cd backend && npm run setup:hypertables
```

### Kafka Setup

```bash
# Start Kafka with Docker
cd infrastructure
docker-compose -f kafka-docker-compose.yml up -d

# Create topics
kafka-topics --create --topic raw-events --bootstrap-server localhost:9092
kafka-topics --create --topic enriched-events --bootstrap-server localhost:9092
kafka-topics --create --topic aggregated-metrics --bootstrap-server localhost:9092
kafka-topics --create --topic ml-features --bootstrap-server localhost:9092
kafka-topics --create --topic user-actions --bootstrap-server localhost:9092
```

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
npm test

# Test specific service
npm run test:backend
npm run test:frontend
npm run test:ml
```

### Integration Tests
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
cd backend && npm run test:integration
```

### End-to-End Tests
```bash
# Start all services
npm run dev

# Run E2E tests
npm run test:e2e
```

### Performance Tests
```bash
# Load testing with Artillery
cd e2e-tests
npm run test:load

# Stress testing
npm run test:stress
```

## 📊 Monitoring

### Application Metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3003 (admin/admin)
- **Health Checks**: http://localhost:3000/health

### Business Metrics
- Dashboard load times
- Widget render times
- ML prediction accuracy
- User engagement rates
- Revenue impact tracking

## 🚢 Deployment

### Docker Deployment
```bash
# Build all images
npm run docker:build

# Start with Docker Compose
npm run docker:up

# Scale services
docker-compose up --scale analytics-api=3 --scale dashboard-api=2
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
npm run k8s:deploy

# Check deployment status
kubectl get pods -l app=analytics-dashboard

# Scale deployment
kubectl scale deployment analytics-api --replicas=5
```

### Production Deployment
```bash
# Build production images
npm run build
docker build -t analytics-dashboard:latest .

# Deploy with blue-green strategy
kubectl apply -f k8s/production/
```

## 📈 Performance

### Benchmarks
- **Dashboard Load Time**: <3 seconds (95th percentile)
- **API Response Time**: <200ms (95th percentile)
- **Concurrent Users**: 10,000+
- **Events Per Second**: 100,000+
- **ML Predictions**: 1,000/second

### Optimization
- Multi-level caching (L1/L2/L3)
- Database query optimization
- CDN for static assets
- Code splitting and lazy loading
- Connection pooling
- Auto-scaling policies

## 🔐 Security

### Authentication
- JWT tokens with 8-hour expiry
- Role-based access control (RBAC)
- Multi-factor authentication support
- OAuth2 integration with Etsy

### Data Protection
- AES-256 encryption at rest
- TLS 1.3 for data in transit
- PII anonymization
- GDPR/CCPA compliance

### Security Measures
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting
- DDoS protection
- Security headers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript strict mode
- Write tests for all new features
- Update documentation
- Follow conventional commits
- Ensure >90% test coverage

## 📝 API Documentation

### Analytics API
- **Swagger UI**: http://localhost:3000/api-docs
- **OpenAPI Spec**: http://localhost:3000/api-json

### Dashboard API
- **GraphQL Playground**: http://localhost:3000/graphql
- **Schema**: http://localhost:3000/graphql-schema

### ML API
- **FastAPI Docs**: http://localhost:8001/docs
- **Redoc**: http://localhost:8001/redoc

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Widget Development](docs/widget-development.md)
- [Deployment Guide](docs/deployment.md)
- [Performance Tuning](docs/performance.md)
- [Security Guidelines](docs/security.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/etsypro/analytics-dashboard/issues)
- **Documentation**: [Wiki](https://github.com/etsypro/analytics-dashboard/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/etsypro/analytics-dashboard/discussions)
- **Email**: support@etsypro.ai

---

Made with ❤️ by the EtsyPro AI Team