import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BullModule } from '@nestjs/bull';
import { CacheModule } from '@nestjs/cache-manager';

// Controllers
import { AnalyticsController } from './controllers/analytics.controller';
import { MetricsController } from './controllers/metrics.controller';
import { ReportsController } from './controllers/reports.controller';

// Services
import { AnalyticsService } from './services/analytics.service';
import { MetricsService } from './services/metrics.service';
import { ReportsService } from './services/reports.service';
import { CacheService } from './services/cache.service';
import { StreamProcessor } from './services/stream-processor.service';

// Entities
import { Metric } from './entities/metric.entity';
import { SalesEvent } from './entities/sales-event.entity';
import { ProductMetric } from './entities/product-metric.entity';
import { UserSession } from './entities/user-session.entity';

// Processors
import { MetricsProcessor } from './processors/metrics.processor';
import { ReportsProcessor } from './processors/reports.processor';

// Kafka Module
import { KafkaModule } from '../kafka/kafka.module';

@Module({
  imports: [
    // TypeORM entities
    TypeOrmModule.forFeature([
      Metric,
      SalesEvent,
      ProductMetric,
      UserSession,
    ]),
    
    // Bull queues
    BullModule.registerQueue(
      {
        name: 'metrics-processing',
        defaultJobOptions: {
          removeOnComplete: 100,
          removeOnFail: 50,
          attempts: 3,
          backoff: {
            type: 'exponential',
            delay: 2000,
          },
        },
      },
      {
        name: 'reports-generation',
        defaultJobOptions: {
          removeOnComplete: 50,
          removeOnFail: 25,
          attempts: 5,
          backoff: {
            type: 'exponential',
            delay: 5000,
          },
        },
      },
    ),

    // Kafka for real-time processing
    KafkaModule,
  ],
  controllers: [
    AnalyticsController,
    MetricsController,
    ReportsController,
  ],
  providers: [
    AnalyticsService,
    MetricsService,
    ReportsService,
    CacheService,
    StreamProcessor,
    MetricsProcessor,
    ReportsProcessor,
  ],
  exports: [
    AnalyticsService,
    MetricsService,
    CacheService,
  ],
})
export class AnalyticsModule {}