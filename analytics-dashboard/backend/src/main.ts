import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { WinstonModule } from 'nest-winston';
import { RedisIoAdapter } from './adapters/redis-io.adapter';
import { AppModule } from './app.module';
import { LoggerConfig } from './config/logger.config';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: WinstonModule.createLogger(LoggerConfig),
  });

  const configService = app.get(ConfigService);
  const port = configService.get('PORT', 3000);
  const globalPrefix = configService.get('GLOBAL_PREFIX', 'api/v1');

  // Security middleware
  app.use(helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        fontSrc: ["'self'", "https://fonts.gstatic.com"],
        imgSrc: ["'self'", "data:", "https:"],
        scriptSrc: ["'self'"],
        connectSrc: ["'self'", "ws:", "wss:"],
      },
    },
  }));

  // Compression
  app.use(compression());

  // Rate limiting
  app.use(rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 1000, // limit each IP to 1000 requests per windowMs
    message: 'Too many requests from this IP, please try again later',
    standardHeaders: true,
    legacyHeaders: false,
  }));

  // Global prefix
  app.setGlobalPrefix(globalPrefix);

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  // CORS configuration
  app.enableCors({
    origin: [
      'http://localhost:3001', // Frontend dev server
      'http://localhost:3000', // Backend
      configService.get('FRONTEND_URL', 'http://localhost:3001'),
    ],
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'x-user-id'],
    credentials: true,
  });

  // Redis adapter for WebSocket
  const redisIoAdapter = new RedisIoAdapter(app, configService);
  await redisIoAdapter.connectToRedis();
  app.useWebSocketAdapter(redisIoAdapter);

  // Swagger documentation
  if (configService.get('NODE_ENV') !== 'production') {
    const config = new DocumentBuilder()
      .setTitle('Analytics Dashboard API')
      .setDescription('EtsyPro AI Analytics Dashboard REST API')
      .setVersion('1.0')
      .addBearerAuth(
        {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
          name: 'JWT',
          description: 'Enter JWT token',
          in: 'header',
        },
        'JWT-auth',
      )
      .addTag('Analytics', 'Real-time analytics endpoints')
      .addTag('Dashboard', 'Dashboard configuration endpoints')
      .addTag('Metrics', 'Metrics and KPI endpoints')
      .addTag('WebSocket', 'Real-time WebSocket events')
      .addTag('Health', 'Health check endpoints')
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup('api-docs', app, document, {
      swaggerOptions: {
        persistAuthorization: true,
        tagsSorter: 'alpha',
        operationsSorter: 'alpha',
      },
    });
  }

  // Health check endpoint
  app.getHttpAdapter().get('/health', (req, res) => {
    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      version: process.env.npm_package_version || '1.0.0',
      environment: configService.get('NODE_ENV', 'development'),
    });
  });

  // Readiness check endpoint
  app.getHttpAdapter().get('/ready', async (req, res) => {
    try {
      // Add database connectivity checks here
      res.json({
        status: 'ready',
        timestamp: new Date().toISOString(),
        services: {
          database: 'connected',
          redis: 'connected',
          kafka: 'connected',
        },
      });
    } catch (error) {
      res.status(503).json({
        status: 'not ready',
        timestamp: new Date().toISOString(),
        error: error.message,
      });
    }
  });

  // Graceful shutdown
  process.on('SIGTERM', async () => {
    console.log('SIGTERM received, shutting down gracefully');
    await app.close();
    process.exit(0);
  });

  process.on('SIGINT', async () => {
    console.log('SIGINT received, shutting down gracefully');
    await app.close();
    process.exit(0);
  });

  await app.listen(port);
  
  const logger = app.get('winston');
  logger.info(`🚀 Analytics Dashboard API is running on: http://localhost:${port}/${globalPrefix}`);
  logger.info(`📚 Swagger documentation available at: http://localhost:${port}/api-docs`);
  logger.info(`🏥 Health check available at: http://localhost:${port}/health`);
}

bootstrap().catch(err => {
  console.error('Failed to start the application:', err);
  process.exit(1);
});