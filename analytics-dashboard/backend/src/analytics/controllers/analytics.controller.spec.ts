import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { getQueueToken } from '@nestjs/bull';
import { AnalyticsController } from './analytics.controller';
import { AnalyticsService } from '../services/analytics.service';
import { MetricsService } from '../services/metrics.service';
import { CacheService } from '../services/cache.service';
import { KafkaProducerService } from '../../kafka/services/kafka-producer.service';
import { Metric } from '../entities/metric.entity';
import { SalesEvent } from '../entities/sales-event.entity';
import { ProductMetric } from '../entities/product-metric.entity';
import { UserSession } from '../entities/user-session.entity';
import { Repository } from 'typeorm';
import { Cache } from 'cache-manager';
import { Queue } from 'bull';

describe('AnalyticsController', () => {
  let controller: AnalyticsController;
  let analyticsService: AnalyticsService;
  let metricsService: MetricsService;

  // Mock data
  const mockUser = {
    sub: 'test-user-123',
    email: 'test@example.com',
    roles: ['user'],
  };

  const mockRealtimeMetrics = {
    timestamp: '2024-01-01T12:00:00Z',
    sales: {
      todayOrders: 15,
      todayRevenue: 1500.00,
      todayItemsSold: 25,
      avgOrderValue: 100.00,
      ordersChange: 12.5,
      revenueChange: 8.3,
    },
    traffic: {
      activeSessions: 3,
      liveVisitors: 3,
    },
    trends: {
      hourlyRevenue: [
        { hour: '2024-01-01T10:00:00Z', revenue: 200 },
        { hour: '2024-01-01T11:00:00Z', revenue: 300 },
        { hour: '2024-01-01T12:00:00Z', revenue: 250 },
      ],
    },
  };

  const mockSalesMetrics = {
    timeframe: 'day',
    period: {
      start: '2024-01-01T00:00:00Z',
      end: '2024-01-01T23:59:59Z',
    },
    summary: {
      totalOrders: 100,
      totalItems: 150,
      totalRevenue: 5000.00,
      avgOrderValue: 50.00,
      minOrderValue: 10.00,
      maxOrderValue: 200.00,
    },
    timeSeries: [
      {
        period: '2024-01-01T10:00:00Z',
        orders: 10,
        items: 15,
        revenue: 500,
      },
    ],
    topProducts: [
      {
        productId: 'prod_123',
        orders: 20,
        quantitySold: 30,
        revenue: 1000,
      },
    ],
  };

  // Mock repositories and services
  const mockRepository = {
    find: jest.fn(),
    findOne: jest.fn(),
    create: jest.fn(),
    save: jest.fn(),
    delete: jest.fn(),
    createQueryBuilder: jest.fn(() => ({
      select: jest.fn().mockReturnThis(),
      where: jest.fn().mockReturnThis(),
      andWhere: jest.fn().mockReturnThis(),
      groupBy: jest.fn().mockReturnThis(),
      orderBy: jest.fn().mockReturnThis(),
      limit: jest.fn().mockReturnThis(),
      getRawOne: jest.fn(),
      getRawMany: jest.fn(),
      getMany: jest.fn(),
    })),
    count: jest.fn(),
  };

  const mockCacheManager = {
    get: jest.fn(),
    set: jest.fn(),
    del: jest.fn(),
    reset: jest.fn(),
  };

  const mockQueue = {
    add: jest.fn(),
    process: jest.fn(),
    getJob: jest.fn(),
    getJobs: jest.fn(),
  };

  const mockCacheService = {
    get: jest.fn(),
    set: jest.fn(),
    del: jest.fn(),
    clear: jest.fn(),
  };

  const mockKafkaProducerService = {
    publishMetricUpdate: jest.fn(),
    publishEvent: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AnalyticsController],
      providers: [
        AnalyticsService,
        MetricsService,
        {
          provide: getRepositoryToken(Metric),
          useValue: mockRepository,
        },
        {
          provide: getRepositoryToken(SalesEvent),
          useValue: mockRepository,
        },
        {
          provide: getRepositoryToken(ProductMetric),
          useValue: mockRepository,
        },
        {
          provide: getRepositoryToken(UserSession),
          useValue: mockRepository,
        },
        {
          provide: getQueueToken('metrics-processing'),
          useValue: mockQueue,
        },
        {
          provide: CACHE_MANAGER,
          useValue: mockCacheManager,
        },
        {
          provide: CacheService,
          useValue: mockCacheService,
        },
        {
          provide: KafkaProducerService,
          useValue: mockKafkaProducerService,
        },
      ],
    }).compile();

    controller = module.get<AnalyticsController>(AnalyticsController);
    analyticsService = module.get<AnalyticsService>(AnalyticsService);
    metricsService = module.get<MetricsService>(MetricsService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getRealtimeMetrics', () => {
    it('should return real-time metrics for authenticated user', async () => {
      // Arrange
      jest.spyOn(analyticsService, 'getRealtimeMetrics').mockResolvedValue(mockRealtimeMetrics);

      // Act
      const result = await controller.getRealtimeMetrics(mockUser);

      // Assert
      expect(result).toEqual(mockRealtimeMetrics);
      expect(analyticsService.getRealtimeMetrics).toHaveBeenCalledWith(mockUser.sub);
    });

    it('should handle errors gracefully', async () => {
      // Arrange
      const errorMessage = 'Database connection failed';
      jest.spyOn(analyticsService, 'getRealtimeMetrics').mockRejectedValue(new Error(errorMessage));

      // Act & Assert
      await expect(controller.getRealtimeMetrics(mockUser)).rejects.toThrow(errorMessage);
    });
  });

  describe('getSalesMetrics', () => {
    const timeframe = 'day';
    const query = {
      start: '2024-01-01T00:00:00Z',
      end: '2024-01-01T23:59:59Z',
    };

    it('should return sales metrics for specified timeframe', async () => {
      // Arrange
      jest.spyOn(analyticsService, 'getSalesMetrics').mockResolvedValue(mockSalesMetrics);

      // Act
      const result = await controller.getSalesMetrics(timeframe, query, mockUser);

      // Assert
      expect(result).toEqual(mockSalesMetrics);
      expect(analyticsService.getSalesMetrics).toHaveBeenCalledWith(
        mockUser.sub,
        timeframe,
        query,
      );
    });

    it('should handle invalid timeframe', async () => {
      // Arrange
      const invalidTimeframe = 'invalid';
      jest.spyOn(analyticsService, 'getSalesMetrics').mockRejectedValue(
        new Error('Invalid timeframe'),
      );

      // Act & Assert
      await expect(
        controller.getSalesMetrics(invalidTimeframe, query, mockUser),
      ).rejects.toThrow('Invalid timeframe');
    });
  });

  describe('getConversionMetrics', () => {
    const productId = 'prod_123';
    const query = { days: 30 };

    it('should return conversion metrics for specific product', async () => {
      // Arrange
      const mockConversionMetrics = {
        period: 30,
        productId: 'prod_123',
        overview: {
          totalViews: 1000,
          totalClicks: 100,
          totalPurchases: 25,
          totalRevenue: 1250.00,
        },
        rates: {
          clickThroughRate: 10.0,
          conversionRate: 2.5,
          purchaseRate: 25.0,
        },
        benchmark: {
          clickThroughRate: 2.5,
          conversionRate: 1.2,
          purchaseRate: 3.8,
        },
        performance: {
          clickThroughRateVsBenchmark: 7.5,
          conversionRateVsBenchmark: 1.3,
          purchaseRateVsBenchmark: 21.2,
        },
        dailyBreakdown: [],
      };

      jest.spyOn(analyticsService, 'getConversionMetrics').mockResolvedValue(mockConversionMetrics);

      // Act
      const result = await controller.getConversionMetrics(productId, query, mockUser);

      // Assert
      expect(result).toEqual(mockConversionMetrics);
      expect(analyticsService.getConversionMetrics).toHaveBeenCalledWith(
        mockUser.sub,
        productId,
        query,
      );
    });

    it('should return overall conversion metrics when no product specified', async () => {
      // Arrange
      const mockOverallMetrics = {
        period: 30,
        productId: null,
        overview: {
          totalViews: 5000,
          totalClicks: 500,
          totalPurchases: 125,
          totalRevenue: 6250.00,
        },
        rates: {
          clickThroughRate: 10.0,
          conversionRate: 2.5,
          purchaseRate: 25.0,
        },
        benchmark: {
          clickThroughRate: 2.5,
          conversionRate: 1.2,
          purchaseRate: 3.8,
        },
        performance: {
          clickThroughRateVsBenchmark: 7.5,
          conversionRateVsBenchmark: 1.3,
          purchaseRateVsBenchmark: 21.2,
        },
        dailyBreakdown: [],
      };

      jest.spyOn(analyticsService, 'getConversionMetrics').mockResolvedValue(mockOverallMetrics);

      // Act
      const result = await controller.getConversionMetrics(undefined, query, mockUser);

      // Assert
      expect(result).toEqual(mockOverallMetrics);
      expect(analyticsService.getConversionMetrics).toHaveBeenCalledWith(
        mockUser.sub,
        undefined,
        query,
      );
    });
  });

  describe('getEngagementMetrics', () => {
    const query = { timeframe: 'month' };

    it('should return engagement metrics', async () => {
      // Arrange
      const mockEngagementMetrics = {
        timeframe: 'month',
        period: {
          start: '2024-01-01T00:00:00Z',
          end: '2024-01-31T23:59:59Z',
        },
        overview: {
          totalSessions: 500,
          uniqueVisitors: 200,
          avgSessionDuration: 180, // 3 minutes
          avgPageViews: 3.5,
          bounceRate: 45.0,
          repeatVisitorRate: 30.0,
        },
        patterns: {
          hourlyDistribution: [
            { hour: 9, sessions: 20, avgDuration: 200 },
            { hour: 14, sessions: 35, avgDuration: 150 },
            { hour: 20, sessions: 30, avgDuration: 180 },
          ],
          peakHours: [14, 20, 9],
        },
        trends: {
          sessionGrowth: 12.5,
          engagementScore: 7.8,
        },
      };

      jest.spyOn(analyticsService, 'getEngagementMetrics').mockResolvedValue(mockEngagementMetrics);

      // Act
      const result = await controller.getEngagementMetrics(query, mockUser);

      // Assert
      expect(result).toEqual(mockEngagementMetrics);
      expect(analyticsService.getEngagementMetrics).toHaveBeenCalledWith(mockUser.sub, query);
    });
  });

  describe('getTrendAnalysis', () => {
    const metric = 'sales';
    const timeframe = 'month';
    const query = {
      start: '2024-01-01T00:00:00Z',
      end: '2024-01-31T23:59:59Z',
    };

    it('should return trend analysis for specified metric', async () => {
      // Arrange
      const mockTrendAnalysis = {
        metric: 'sales',
        timeframe: 'month',
        period: {
          start: '2024-01-01T00:00:00Z',
          end: '2024-01-31T23:59:59Z',
        },
        trend: {
          direction: 'up',
          strength: 0.75,
          changePercent: 12.5,
          significance: 'moderate',
        },
        dataPoints: [],
        insights: ['Positive trend detected', 'Above industry average'],
        recommendations: ['Continue current strategy', 'Monitor closely'],
      };

      jest.spyOn(analyticsService, 'getTrendAnalysis').mockResolvedValue(mockTrendAnalysis);

      // Act
      const result = await controller.getTrendAnalysis(metric, timeframe, query, mockUser);

      // Assert
      expect(result).toEqual(mockTrendAnalysis);
      expect(analyticsService.getTrendAnalysis).toHaveBeenCalledWith(
        mockUser.sub,
        metric,
        timeframe,
        query,
      );
    });
  });

  describe('refreshMetrics', () => {
    it('should refresh user metrics and return success', async () => {
      // Arrange
      jest.spyOn(metricsService, 'refreshUserMetrics').mockResolvedValue(undefined);

      // Act
      const result = await controller.refreshMetrics(mockUser);

      // Assert
      expect(result).toEqual({ success: true });
      expect(metricsService.refreshUserMetrics).toHaveBeenCalledWith(mockUser.sub);
    });

    it('should handle refresh errors', async () => {
      // Arrange
      const errorMessage = 'Failed to refresh metrics';
      jest.spyOn(metricsService, 'refreshUserMetrics').mockRejectedValue(new Error(errorMessage));

      // Act & Assert
      await expect(controller.refreshMetrics(mockUser)).rejects.toThrow(errorMessage);
    });
  });

  describe('exportData', () => {
    const format = 'csv';
    const query = {
      metrics: 'sales,conversion,engagement',
      start: '2024-01-01',
      end: '2024-01-31',
    };

    it('should initiate data export and return export info', async () => {
      // Arrange
      const mockExportResult = {
        exportId: 'export_test-user-123_1704110400000',
        downloadUrl: '/api/v1/exports/export_test-user-123_1704110400000',
      };

      jest.spyOn(analyticsService, 'exportData').mockResolvedValue(mockExportResult);

      // Act
      const result = await controller.exportData(format, query, mockUser);

      // Assert
      expect(result).toEqual(mockExportResult);
      expect(analyticsService.exportData).toHaveBeenCalledWith(mockUser.sub, format, query);
    });

    it('should handle invalid export format', async () => {
      // Arrange
      const invalidFormat = 'invalid';
      jest.spyOn(analyticsService, 'exportData').mockRejectedValue(
        new Error('Invalid export format'),
      );

      // Act & Assert
      await expect(
        controller.exportData(invalidFormat, query, mockUser),
      ).rejects.toThrow('Invalid export format');
    });
  });

  describe('executeCustomQuery', () => {
    it('should execute custom query for enterprise users', async () => {
      // Arrange
      const customQuery = {
        query: 'SELECT COUNT(*) FROM sales_events WHERE user_id = ?',
        parameters: [mockUser.sub],
        format: 'json',
      };

      const mockQueryResult = {
        query: customQuery,
        results: [{ count: 100 }],
        executionTime: '0.123s',
        rowCount: 1,
      };

      jest.spyOn(analyticsService, 'executeCustomQuery').mockResolvedValue(mockQueryResult);

      // Act
      const result = await controller.executeCustomQuery(customQuery, mockUser);

      // Assert
      expect(result).toEqual(mockQueryResult);
      expect(analyticsService.executeCustomQuery).toHaveBeenCalledWith(mockUser.sub, customQuery);
    });

    it('should reject malicious queries', async () => {
      // Arrange
      const maliciousQuery = {
        query: 'DROP TABLE users; --',
        parameters: [],
        format: 'json',
      };

      jest.spyOn(analyticsService, 'executeCustomQuery').mockRejectedValue(
        new Error('Query contains forbidden keyword: DROP'),
      );

      // Act & Assert
      await expect(
        controller.executeCustomQuery(maliciousQuery, mockUser),
      ).rejects.toThrow('Query contains forbidden keyword: DROP');
    });
  });

  describe('Input Validation', () => {
    it('should validate timeframe parameter', async () => {
      // This would be handled by NestJS validation pipes
      // Testing the service layer validation instead
      const invalidTimeframe = 'invalid_timeframe';
      
      jest.spyOn(analyticsService, 'getSalesMetrics').mockRejectedValue(
        new Error('Invalid timeframe parameter'),
      );

      await expect(
        controller.getSalesMetrics(invalidTimeframe, {}, mockUser),
      ).rejects.toThrow('Invalid timeframe parameter');
    });

    it('should validate date range parameters', async () => {
      const invalidQuery = {
        start: 'invalid-date',
        end: 'also-invalid',
      };

      jest.spyOn(analyticsService, 'getSalesMetrics').mockRejectedValue(
        new Error('Invalid date format'),
      );

      await expect(
        controller.getSalesMetrics('day', invalidQuery, mockUser),
      ).rejects.toThrow('Invalid date format');
    });
  });

  describe('Error Handling', () => {
    it('should handle database connection errors', async () => {
      // Arrange
      jest.spyOn(analyticsService, 'getRealtimeMetrics').mockRejectedValue(
        new Error('Database connection failed'),
      );

      // Act & Assert
      await expect(controller.getRealtimeMetrics(mockUser)).rejects.toThrow(
        'Database connection failed',
      );
    });

    it('should handle rate limiting errors', async () => {
      // Arrange
      jest.spyOn(analyticsService, 'getRealtimeMetrics').mockRejectedValue(
        new Error('Rate limit exceeded'),
      );

      // Act & Assert
      await expect(controller.getRealtimeMetrics(mockUser)).rejects.toThrow(
        'Rate limit exceeded',
      );
    });
  });
});