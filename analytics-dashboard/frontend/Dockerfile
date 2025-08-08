# Analytics Dashboard Frontend - Multi-stage Dockerfile

# ===================
# Base Stage
# ===================
FROM node:18-alpine AS base

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    libc6-compat

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# ===================
# Development Stage
# ===================
FROM base AS development

# Install all dependencies (including devDependencies)
RUN npm ci --include=dev

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S react -u 1001

# Change ownership of the app directory
RUN chown -R react:nodejs /app && \
    mkdir -p /app/node_modules/.cache && \
    chown -R react:nodejs /app/node_modules/.cache

# Switch to non-root user
USER react

# Expose port
EXPOSE 3001

# Set environment variables
ENV GENERATE_SOURCEMAP=false
ENV FAST_REFRESH=true
ENV WDS_SOCKET_HOST=localhost
ENV WDS_SOCKET_PORT=3001

# Start the development server
CMD ["npm", "start"]

# ===================
# Build Stage
# ===================
FROM base AS build

# Install all dependencies
RUN npm ci --include=dev

# Copy source code
COPY . .

# Set build environment variables
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false
ENV INLINE_RUNTIME_CHUNK=false

# Build the application
RUN npm run build

# ===================
# Production Stage
# ===================
FROM nginx:1.25-alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built React app from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

# Create nginx user and set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# ===================
# Testing Stage
# ===================
FROM development AS testing

# Copy test configuration
COPY --chown=react:nodejs jest.config.js ./
COPY --chown=react:nodejs src/ ./src/

# Run tests
CMD ["npm", "run", "test:ci"]

# ===================
# Build Analyzer Stage
# ===================
FROM build AS analyzer

# Install additional analysis tools
RUN npm install -g webpack-bundle-analyzer

# Copy built files
COPY --from=build /app/build ./build

# Run bundle analysis
CMD ["npm", "run", "analyze"]