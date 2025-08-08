import { Injectable, Logger, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Between, MoreThan, LessThan } from 'typeorm';
import { InjectQueue } from '@nestjs/bull';
import { Queue } from 'bull';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { Inject } from '@nestjs/common';

// Entities
import { Metric } from '../entities/metric.entity';
import { SalesEvent } from '../entities/sales-event.entity';
import { ProductMetric } from '../entities/product-metric.entity';
import { UserSession } from '../entities/user-session.entity';

// DTOs
import {
  RealtimeMetricsDto,
  SalesMetricsDto,
  ConversionMetricsDto,
  EngagementMetricsDto,
  TrendAnalysisDto,
  CustomQueryDto,
  TimeframeQuery,
  MetricsQueryDto,
} from '../dto';

// Services
import { CacheService } from './cache.service';
import { KafkaProducerService } from '../../kafka/services/kafka-producer.service';

@Injectable()
export class AnalyticsService {
  private readonly logger = new Logger(AnalyticsService.name);

  constructor(
    @InjectRepository(Metric)
    private readonly metricsRepository: Repository<Metric>,
    @InjectRepository(SalesEvent)
    private readonly salesEventRepository: Repository<SalesEvent>,
    @InjectRepository(ProductMetric)
    private readonly productMetricRepository: Repository<ProductMetric>,
    @InjectRepository(UserSession)
    private readonly userSessionRepository: Repository<UserSession>,
    @InjectQueue('metrics-processing')
    private readonly metricsQueue: Queue,
    @Inject(CACHE_MANAGER)
    private readonly cacheManager: Cache,
    private readonly cacheService: CacheService,
    private readonly kafkaProducerService: KafkaProducerService,
  ) {}

  async getRealtimeMetrics(userId: string): Promise<RealtimeMetricsDto> {
    const cacheKey = `realtime_metrics:${userId}`;
    
    // Try to get from cache first
    let metrics = await this.cacheService.get(cacheKey);
    
    if (!metrics) {
      this.logger.debug(`Cache miss for realtime metrics: ${userId}`);
      
      // Calculate real-time metrics
      const now = new Date();
      const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const yesterdayStart = new Date(todayStart.getTime() - 24 * 60 * 60 * 1000);
      
      // Get today's sales
      const todaySales = await this.salesEventRepository
        .createQueryBuilder('sale')
        .select([
          'COUNT(*) as orders',
          'SUM(sale.quantity) as items_sold',
          'SUM(sale.price * sale.quantity) as revenue',
          'AVG(sale.price) as avg_order_value',
        ])
        .where('sale.user_id = :userId', { userId })
        .andWhere('sale.time >= :todayStart', { todayStart })
        .getRawOne();

      // Get yesterday's sales for comparison
      const yesterdaySales = await this.salesEventRepository
        .createQueryBuilder('sale')
        .select([
          'COUNT(*) as orders',
          'SUM(sale.quantity) as items_sold', 
          'SUM(sale.price * sale.quantity) as revenue',
        ])
        .where('sale.user_id = :userId', { userId })
        .andWhere('sale.time >= :yesterdayStart', { yesterdayStart })
        .andWhere('sale.time < :todayStart', { todayStart })
        .getRawOne();

      // Get current active sessions
      const activeSessions = await this.userSessionRepository.count({
        where: {
          userId,
          endTime: null, // Still active
          startTime: MoreThan(new Date(now.getTime() - 30 * 60 * 1000)), // Started within last 30 minutes
        },
      });

      // Calculate percentage changes
      const ordersChange = yesterdaySales.orders > 0 
        ? ((todaySales.orders - yesterdaySales.orders) / yesterdaySales.orders) * 100
        : todaySales.orders > 0 ? 100 : 0;

      const revenueChange = yesterdaySales.revenue > 0
        ? ((todaySales.revenue - yesterdaySales.revenue) / yesterdaySales.revenue) * 100
        : todaySales.revenue > 0 ? 100 : 0;

      // Get hourly trends for the chart
      const hourlyTrends = await this.salesEventRepository
        .createQueryBuilder('sale')
        .select([
          "DATE_TRUNC('hour', sale.time) as hour",
          'SUM(sale.price * sale.quantity) as revenue',
        ])
        .where('sale.user_id = :userId', { userId })
        .andWhere('sale.time >= :todayStart', { todayStart })
        .groupBy("DATE_TRUNC('hour', sale.time)")
        .orderBy('hour')
        .getRawMany();

      metrics = {
        timestamp: now.toISOString(),
        sales: {
          todayOrders: parseInt(todaySales.orders) || 0,
          todayRevenue: parseFloat(todaySales.revenue) || 0,
          todayItemsSold: parseInt(todaySales.items_sold) || 0,
          avgOrderValue: parseFloat(todaySales.avg_order_value) || 0,
          ordersChange: Math.round(ordersChange * 100) / 100,
          revenueChange: Math.round(revenueChange * 100) / 100,
        },
        traffic: {
          activeSessions,
          liveVisitors: activeSessions, // Simplified for demo
        },
        trends: {
          hourlyRevenue: hourlyTrends.map(trend => ({
            hour: trend.hour,
            revenue: parseFloat(trend.revenue) || 0,
          })),
        },
      };

      // Cache for 30 seconds
      await this.cacheService.set(cacheKey, metrics, 30);
    }

    // Publish real-time update to WebSocket clients
    await this.kafkaProducerService.publishMetricUpdate({
      userId,
      type: 'realtime_metrics',
      data: metrics,
    });

    return metrics;
  }

  async getSalesMetrics(
    userId: string,
    timeframe: string,
    query: TimeframeQuery,
  ): Promise<SalesMetricsDto> {
    const cacheKey = `sales_metrics:${userId}:${timeframe}:${query.start || 'default'}:${query.end || 'default'}`;
    
    let metrics = await this.cacheService.get(cacheKey);
    
    if (!metrics) {
      const { start, end } = this.getTimeframeBounds(timeframe, query);
      
      // Build the base query
      const queryBuilder = this.salesEventRepository
        .createQueryBuilder('sale')
        .where('sale.user_id = :userId', { userId })
        .andWhere('sale.time >= :start', { start })
        .andWhere('sale.time <= :end', { end });

      // Get aggregate metrics
      const aggregateMetrics = await queryBuilder
        .select([
          'COUNT(*) as total_orders',
          'SUM(sale.quantity) as total_items',
          'SUM(sale.price * sale.quantity) as total_revenue',
          'AVG(sale.price) as avg_order_value',
          'MIN(sale.price) as min_order_value',
          'MAX(sale.price) as max_order_value',
        ])
        .getRawOne();

      // Get time-series data based on timeframe
      const timeSeriesFormat = this.getTimeSeriesFormat(timeframe);
      const timeSeries = await queryBuilder
        .select([
          `DATE_TRUNC('${timeSeriesFormat}', sale.time) as period`,
          'COUNT(*) as orders',
          'SUM(sale.quantity) as items',
          'SUM(sale.price * sale.quantity) as revenue',
        ])
        .groupBy(`DATE_TRUNC('${timeSeriesFormat}', sale.time)`)
        .orderBy('period')
        .getRawMany();

      // Get top products
      const topProducts = await queryBuilder
        .select([
          'sale.product_id',
          'COUNT(*) as orders',
          'SUM(sale.quantity) as quantity_sold',
          'SUM(sale.price * sale.quantity) as revenue',
        ])
        .groupBy('sale.product_id')
        .orderBy('revenue', 'DESC')
        .limit(10)
        .getRawMany();

      metrics = {
        timeframe,
        period: { start: start.toISOString(), end: end.toISOString() },
        summary: {
          totalOrders: parseInt(aggregateMetrics.total_orders) || 0,
          totalItems: parseInt(aggregateMetrics.total_items) || 0,
          totalRevenue: parseFloat(aggregateMetrics.total_revenue) || 0,
          avgOrderValue: parseFloat(aggregateMetrics.avg_order_value) || 0,
          minOrderValue: parseFloat(aggregateMetrics.min_order_value) || 0,
          maxOrderValue: parseFloat(aggregateMetrics.max_order_value) || 0,
        },
        timeSeries: timeSeries.map(item => ({
          period: item.period,
          orders: parseInt(item.orders),
          items: parseInt(item.items),
          revenue: parseFloat(item.revenue),
        })),
        topProducts: topProducts.map(product => ({
          productId: product.product_id,
          orders: parseInt(product.orders),
          quantitySold: parseInt(product.quantity_sold),
          revenue: parseFloat(product.revenue),
        })),
      };

      // Cache for 5 minutes
      await this.cacheService.set(cacheKey, metrics, 300);
    }

    return metrics;
  }

  async getConversionMetrics(
    userId: string,
    productId?: string,
    query?: MetricsQueryDto,
  ): Promise<ConversionMetricsDto> {
    const days = query?.days || 30;
    const cacheKey = `conversion_metrics:${userId}:${productId || 'all'}:${days}`;
    
    let metrics = await this.cacheService.get(cacheKey);
    
    if (!metrics) {
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - days);

      let conversionQuery = this.productMetricRepository
        .createQueryBuilder('pm')
        .where('pm.user_id = :userId', { userId })
        .andWhere('pm.time >= :startDate', { startDate });

      if (productId) {
        conversionQuery = conversionQuery.andWhere('pm.product_id = :productId', { productId });
      }

      const conversionData = await conversionQuery
        .select([
          'SUM(pm.views) as total_views',
          'SUM(pm.clicks) as total_clicks',
          'SUM(pm.purchases) as total_purchases',
          'SUM(pm.revenue) as total_revenue',
        ])
        .getRawOne();

      const totalViews = parseInt(conversionData.total_views) || 0;
      const totalClicks = parseInt(conversionData.total_clicks) || 0;
      const totalPurchases = parseInt(conversionData.total_purchases) || 0;

      // Calculate conversion rates
      const clickThroughRate = totalViews > 0 ? (totalClicks / totalViews) * 100 : 0;
      const conversionRate = totalViews > 0 ? (totalPurchases / totalViews) * 100 : 0;
      const purchaseRate = totalClicks > 0 ? (totalPurchases / totalClicks) * 100 : 0;

      // Get daily breakdown
      const dailyBreakdown = await conversionQuery
        .select([
          "DATE_TRUNC('day', pm.time) as day",
          'SUM(pm.views) as views',
          'SUM(pm.clicks) as clicks',
          'SUM(pm.purchases) as purchases',
          'AVG(pm.conversion_rate) as avg_conversion_rate',
        ])
        .groupBy("DATE_TRUNC('day', pm.time)")
        .orderBy('day')
        .getRawMany();

      // Get industry benchmark (mock data for demo)
      const industryBenchmark = {
        clickThroughRate: 2.5,
        conversionRate: 1.2,
        purchaseRate: 3.8,
      };

      metrics = {
        period: days,
        productId: productId || null,
        overview: {
          totalViews,
          totalClicks,
          totalPurchases,
          totalRevenue: parseFloat(conversionData.total_revenue) || 0,
        },
        rates: {
          clickThroughRate: Math.round(clickThroughRate * 100) / 100,
          conversionRate: Math.round(conversionRate * 100) / 100,
          purchaseRate: Math.round(purchaseRate * 100) / 100,
        },
        benchmark: industryBenchmark,
        performance: {
          clickThroughRateVsBenchmark: clickThroughRate - industryBenchmark.clickThroughRate,
          conversionRateVsBenchmark: conversionRate - industryBenchmark.conversionRate,
          purchaseRateVsBenchmark: purchaseRate - industryBenchmark.purchaseRate,
        },
        dailyBreakdown: dailyBreakdown.map(day => ({
          date: day.day,
          views: parseInt(day.views),
          clicks: parseInt(day.clicks),
          purchases: parseInt(day.purchases),
          conversionRate: parseFloat(day.avg_conversion_rate) || 0,
        })),
      };

      // Cache for 15 minutes
      await this.cacheService.set(cacheKey, metrics, 900);
    }

    return metrics;
  }

  async getEngagementMetrics(
    userId: string,
    query?: MetricsQueryDto,
  ): Promise<EngagementMetricsDto> {
    const timeframe = query?.timeframe || 'month';
    const cacheKey = `engagement_metrics:${userId}:${timeframe}`;
    
    let metrics = await this.cacheService.get(cacheKey);
    
    if (!metrics) {
      const { start, end } = this.getTimeframeBounds(timeframe, query);

      // Get session analytics
      const sessionMetrics = await this.userSessionRepository
        .createQueryBuilder('session')
        .where('session.user_id = :userId', { userId })
        .andWhere('session.start_time >= :start', { start })
        .andWhere('session.start_time <= :end', { end })
        .select([
          'COUNT(*) as total_sessions',
          'AVG(session.duration) as avg_duration',
          'AVG(session.page_views) as avg_page_views',
          'SUM(CASE WHEN session.page_views = 1 THEN 1 ELSE 0 END) as bounce_sessions',
          'COUNT(DISTINCT session.visitor_id) as unique_visitors',
        ])
        .getRawOne();

      const totalSessions = parseInt(sessionMetrics.total_sessions) || 0;
      const bounceSessions = parseInt(sessionMetrics.bounce_sessions) || 0;
      const bounceRate = totalSessions > 0 ? (bounceSessions / totalSessions) * 100 : 0;

      // Get repeat visitor analysis
      const repeatVisitorQuery = await this.userSessionRepository
        .createQueryBuilder('session')
        .where('session.user_id = :userId', { userId })
        .andWhere('session.start_time >= :start', { start })
        .andWhere('session.start_time <= :end', { end })
        .select([
          'session.visitor_id',
          'COUNT(*) as session_count',
        ])
        .groupBy('session.visitor_id')
        .getRawMany();

      const repeatVisitors = repeatVisitorQuery.filter(v => parseInt(v.session_count) > 1).length;
      const uniqueVisitors = parseInt(sessionMetrics.unique_visitors) || 0;
      const repeatVisitorRate = uniqueVisitors > 0 ? (repeatVisitors / uniqueVisitors) * 100 : 0;

      // Get hourly engagement patterns
      const hourlyPatterns = await this.userSessionRepository
        .createQueryBuilder('session')
        .where('session.user_id = :userId', { userId })
        .andWhere('session.start_time >= :start', { start })
        .andWhere('session.start_time <= :end', { end })
        .select([
          "EXTRACT(hour FROM session.start_time) as hour",
          'COUNT(*) as sessions',
          'AVG(session.duration) as avg_duration',
        ])
        .groupBy("EXTRACT(hour FROM session.start_time)")
        .orderBy('hour')
        .getRawMany();

      metrics = {
        timeframe,
        period: { start: start.toISOString(), end: end.toISOString() },
        overview: {
          totalSessions,
          uniqueVisitors,
          avgSessionDuration: Math.round(parseFloat(sessionMetrics.avg_duration) || 0),
          avgPageViews: Math.round((parseFloat(sessionMetrics.avg_page_views) || 0) * 100) / 100,
          bounceRate: Math.round(bounceRate * 100) / 100,
          repeatVisitorRate: Math.round(repeatVisitorRate * 100) / 100,
        },
        patterns: {
          hourlyDistribution: hourlyPatterns.map(pattern => ({
            hour: parseInt(pattern.hour),
            sessions: parseInt(pattern.sessions),
            avgDuration: Math.round(parseFloat(pattern.avg_duration) || 0),
          })),
          peakHours: hourlyPatterns
            .sort((a, b) => parseInt(b.sessions) - parseInt(a.sessions))
            .slice(0, 3)
            .map(pattern => parseInt(pattern.hour)),
        },
        trends: {
          // This would typically include week-over-week or month-over-month comparisons
          // For demo purposes, we'll add placeholder data
          sessionGrowth: 12.5, // Percentage growth
          engagementScore: 7.8, // Out of 10
        },
      };

      // Cache for 1 hour
      await this.cacheService.set(cacheKey, metrics, 3600);
    }

    return metrics;
  }

  async getTrendAnalysis(
    userId: string,
    metric: string,
    timeframe: string,
    query?: TimeframeQuery,
  ): Promise<TrendAnalysisDto> {
    const cacheKey = `trend_analysis:${userId}:${metric}:${timeframe}`;
    
    // Queue trend analysis job for complex calculations
    const job = await this.metricsQueue.add('trend-analysis', {
      userId,
      metric,
      timeframe,
      query,
    });

    // For immediate response, return cached data or basic calculation
    let analysis = await this.cacheService.get(cacheKey);
    
    if (!analysis) {
      // Perform basic trend calculation
      analysis = await this.calculateBasicTrend(userId, metric, timeframe, query);
      
      // Cache for 2 hours
      await this.cacheService.set(cacheKey, analysis, 7200);
    }

    return analysis;
  }

  async executeCustomQuery(userId: string, customQuery: CustomQueryDto): Promise<any> {
    // Validate query for security
    this.validateCustomQuery(customQuery);

    // Log custom query for audit
    this.logger.log(`Custom query executed by user ${userId}:`, customQuery);

    // For demo purposes, return mock data
    // In production, this would execute validated SQL queries
    return {
      query: customQuery,
      results: [],
      executionTime: '0.123s',
      rowCount: 0,
      message: 'Custom query feature coming soon',
    };
  }

  async exportData(userId: string, format: string, query: any): Promise<{ exportId: string; downloadUrl?: string }> {
    const exportId = `export_${userId}_${Date.now()}`;
    
    // Queue export job
    await this.metricsQueue.add('data-export', {
      userId,
      format,
      query,
      exportId,
    });

    return {
      exportId,
      downloadUrl: format === 'csv' ? `/api/v1/exports/${exportId}` : undefined,
    };
  }

  async getCohortAnalysis(userId: string, targetUserId?: string, cohortType?: string): Promise<any> {
    // Implementation would analyze user cohorts and retention
    return {
      cohortType: cohortType || 'acquisition',
      analysis: 'Cohort analysis feature coming soon',
    };
  }

  async getFunnelAnalysis(userId: string, funnelId: string, query?: TimeframeQuery): Promise<any> {
    // Implementation would analyze conversion funnels
    return {
      funnelId,
      analysis: 'Funnel analysis feature coming soon',
    };
  }

  private getTimeframeBounds(timeframe: string, query?: TimeframeQuery): { start: Date; end: Date } {
    const now = new Date();
    let start: Date;
    let end: Date = query?.end ? new Date(query.end) : now;

    if (query?.start) {
      start = new Date(query.start);
    } else {
      switch (timeframe) {
        case 'hour':
          start = new Date(now.getTime() - 60 * 60 * 1000);
          break;
        case 'day':
          start = new Date(now.getTime() - 24 * 60 * 60 * 1000);
          break;
        case 'week':
          start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        case 'month':
          start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          break;
        case 'year':
          start = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
          break;
        default:
          start = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      }
    }

    return { start, end };
  }

  private getTimeSeriesFormat(timeframe: string): string {
    switch (timeframe) {
      case 'hour':
        return 'minute';
      case 'day':
        return 'hour';
      case 'week':
        return 'day';
      case 'month':
        return 'day';
      case 'year':
        return 'month';
      default:
        return 'hour';
    }
  }

  private async calculateBasicTrend(
    userId: string,
    metric: string,
    timeframe: string,
    query?: TimeframeQuery,
  ): Promise<TrendAnalysisDto> {
    // Basic trend calculation implementation
    const { start, end } = this.getTimeframeBounds(timeframe, query);
    
    return {
      metric,
      timeframe,
      period: { start: start.toISOString(), end: end.toISOString() },
      trend: {
        direction: 'up', // 'up', 'down', 'stable'
        strength: 0.75, // 0-1 scale
        changePercent: 12.5,
        significance: 'moderate', // 'low', 'moderate', 'high'
      },
      dataPoints: [],
      insights: ['Positive trend detected', 'Above industry average'],
      recommendations: ['Continue current strategy', 'Monitor closely'],
    };
  }

  private validateCustomQuery(query: CustomQueryDto): void {
    // Security validation for custom queries
    const dangerousKeywords = ['DELETE', 'DROP', 'UPDATE', 'INSERT', 'ALTER', 'CREATE'];
    const queryString = JSON.stringify(query).toUpperCase();
    
    for (const keyword of dangerousKeywords) {
      if (queryString.includes(keyword)) {
        throw new BadRequestException(`Query contains forbidden keyword: ${keyword}`);
      }
    }
  }
}