# Deployment Guide - EtsyPro AI Authentication Service

## Overview

This guide covers the deployment process for the EtsyPro AI Authentication Service across different environments.

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3.x (optional)
- Docker registry access
- PostgreSQL database
- Redis cluster
- SSL certificates
- External service credentials (Etsy, SendGrid, Twilio)

## Environment Setup

### 1. Development Environment

```bash
# Install dependencies
npm install

# Set up local database
docker run -d \
  --name etsypro-postgres \
  -e POSTGRES_DB=etsypro_auth \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine

# Set up Redis
docker run -d \
  --name etsypro-redis \
  -p 6379:6379 \
  redis:7-alpine

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
npm run migration:run

# Start service
npm run dev
```

### 2. Staging Environment

```bash
# Build Docker image
docker build -t etsypro/auth-service:staging .

# Push to registry
docker push etsypro/auth-service:staging

# Deploy to Kubernetes
kubectl apply -f k8s/staging/ -n etsypro-staging
```

### 3. Production Environment

## Pre-deployment Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance tests meet SLA
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured
- [ ] Load balancer health checks verified
- [ ] SSL certificates valid
- [ ] Secrets rotated

## Deployment Steps

### Step 1: Database Migration

```bash
# Connect to production database
kubectl run -it --rm --image=postgres:15-alpine psql \
  --env="PGPASSWORD=$DB_PASSWORD" \
  -- psql -h $DB_HOST -U $DB_USER -d etsypro_auth

# Run migrations
npm run migration:production
```

### Step 2: Update Secrets

```bash
# Create/update secrets
kubectl create secret generic auth-jwt-secret \
  --from-literal=secret=$(openssl rand -base64 32) \
  --from-literal=refresh-secret=$(openssl rand -base64 32) \
  -n etsypro \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic etsy-oauth-secret \
  --from-literal=client-id=$ETSY_CLIENT_ID \
  --from-literal=client-secret=$ETSY_CLIENT_SECRET \
  -n etsypro \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Step 3: Deploy Application

```bash
# Build and push production image
docker build -t etsypro/auth-service:v1.0.0 .
docker push etsypro/auth-service:v1.0.0

# Update image in deployment
kubectl set image deployment/auth-service \
  auth-service=etsypro/auth-service:v1.0.0 \
  -n etsypro

# Monitor rollout
kubectl rollout status deployment/auth-service -n etsypro
```

### Step 4: Verify Deployment

```bash
# Check pod status
kubectl get pods -n etsypro -l app=auth-service

# Check logs
kubectl logs -f deployment/auth-service -n etsypro

# Test health endpoint
kubectl port-forward service/auth-service 3001:80 -n etsypro
curl http://localhost:3001/api/v1/health

# Run smoke tests
npm run test:smoke
```

## Blue-Green Deployment

```bash
# Deploy green version
kubectl apply -f k8s/deployment-green.yaml -n etsypro

# Wait for green to be ready
kubectl wait --for=condition=ready pod -l version=green -n etsypro

# Switch traffic to green
kubectl patch service auth-service -n etsypro \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Remove blue deployment
kubectl delete deployment auth-service-blue -n etsypro
```

## Canary Deployment

```bash
# Deploy canary version (10% traffic)
kubectl apply -f k8s/deployment-canary.yaml -n etsypro

# Monitor metrics
# If successful, gradually increase traffic

# Update to 50% traffic
kubectl patch virtualservice auth-service -n etsypro \
  --type merge \
  -p '{"spec":{"http":[{"weight":50,"destination":{"subset":"canary"}}]}}'

# Complete rollout
kubectl set image deployment/auth-service \
  auth-service=etsypro/auth-service:canary \
  -n etsypro
```

## Rollback Procedure

```bash
# Quick rollback to previous version
kubectl rollout undo deployment/auth-service -n etsypro

# Rollback to specific revision
kubectl rollout history deployment/auth-service -n etsypro
kubectl rollout undo deployment/auth-service --to-revision=2 -n etsypro

# Database rollback (if needed)
npm run migration:revert
```

## Configuration Management

### Environment Variables

Production values stored in Kubernetes secrets and configmaps:

```yaml
# Required secrets
- auth-jwt-secret
- auth-db-secret
- etsy-oauth-secret
- sendgrid-secret
- twilio-secret

# Configurable values
- auth-config (ConfigMap)
```

### Feature Flags

```javascript
// Feature flags in ConfigMap
{
  "features": {
    "mfa_sms": true,
    "mfa_totp": true,
    "oauth_etsy": true,
    "rate_limiting": true,
    "session_tracking": true
  }
}
```

## Monitoring & Alerts

### Key Metrics

```yaml
# Prometheus rules
- name: auth_service_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"
      
  - alert: SlowResponseTime
    expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 0.5
    for: 5m
    annotations:
      summary: "95th percentile response time > 500ms"
      
  - alert: LowLoginSuccessRate
    expr: rate(auth_login_success_total[5m]) / rate(auth_login_attempts_total[5m]) < 0.95
    for: 5m
    annotations:
      summary: "Login success rate below 95%"
```

### Dashboards

Import Grafana dashboards:
- `dashboards/auth-service-overview.json`
- `dashboards/auth-service-security.json`
- `dashboards/auth-service-performance.json`

## Security Considerations

### Pre-deployment Security Scan

```bash
# Run security scan
npm audit
docker scan etsypro/auth-service:latest

# OWASP dependency check
dependency-check --project auth-service --scan .

# Kubernetes security policies
kubectl apply -f k8s/security-policies/
```

### Secret Rotation

```bash
# Rotate JWT secret (zero-downtime)
# 1. Add new secret to existing ones
kubectl patch secret auth-jwt-secret -n etsypro \
  --type merge \
  -p '{"data":{"new-secret":"'$(echo -n $NEW_SECRET | base64)'"}}'

# 2. Update application to accept both secrets
# 3. Switch to new secret only
# 4. Remove old secret
```

## Disaster Recovery

### Backup Strategy

```bash
# Database backup
pg_dump -h $DB_HOST -U $DB_USER -d etsypro_auth > backup_$(date +%Y%m%d).sql

# Redis backup
redis-cli --rdb /backup/dump.rdb

# Kubernetes resources
kubectl get all,secrets,configmaps -n etsypro -o yaml > k8s-backup.yaml
```

### Recovery Procedures

1. **Database Recovery**
   ```bash
   psql -h $DB_HOST -U $DB_USER -d etsypro_auth < backup.sql
   ```

2. **Redis Recovery**
   ```bash
   redis-cli --pipe < dump.rdb
   ```

3. **Full Service Recovery**
   ```bash
   kubectl apply -f k8s-backup.yaml
   ```

## Performance Tuning

### Application Tuning

```javascript
// Optimize for production
{
  "node": {
    "max_old_space_size": 512,
    "max_http_header_size": 16384
  },
  "clustering": {
    "workers": "auto", // CPU cores
    "restart_on_failure": true
  },
  "database": {
    "pool_size": 20,
    "statement_timeout": 30000
  }
}
```

### Kubernetes Resources

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Check memory usage
   kubectl top pods -n etsypro
   
   # Get heap dump
   kubectl exec -it <pod> -n etsypro -- kill -USR2 1
   ```

2. **Database Connection Issues**
   ```bash
   # Check connection pool
   kubectl exec -it <pod> -n etsypro -- npm run db:health
   ```

3. **Redis Connection Issues**
   ```bash
   # Test Redis connection
   kubectl exec -it <pod> -n etsypro -- redis-cli ping
   ```

### Debug Mode

```bash
# Enable debug logging
kubectl set env deployment/auth-service DEBUG=auth:* -n etsypro

# View detailed logs
kubectl logs -f deployment/auth-service -n etsypro --tail=100
```

## Post-Deployment

### Smoke Tests

```bash
# Run automated smoke tests
npm run test:smoke:production

# Manual verification checklist
- [ ] Login endpoint responding
- [ ] OAuth flow working
- [ ] MFA enrollment functional
- [ ] Password reset emails sending
- [ ] Session management working
- [ ] Rate limiting active
```

### Performance Validation

```bash
# Run load test
k6 run -e BASE_URL=https://api.etsypro.ai performance-test.js

# Verify SLOs
- [ ] 95th percentile < 500ms
- [ ] Error rate < 5%
- [ ] 10K concurrent users supported
```

## Support

- **Oncall**: #auth-service-oncall
- **Runbook**: wiki/auth-service-runbook
- **Escalation**: security@etsypro.ai