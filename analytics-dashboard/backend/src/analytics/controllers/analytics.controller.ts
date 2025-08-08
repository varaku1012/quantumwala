import {
  Controller,
  Get,
  Post,
  Body,
  Query,
  Param,
  UseGuards,
  HttpStatus,
  HttpCode,
  ParseUUIDPipe,
  ValidationPipe,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiQuery,
  ApiParam,
} from '@nestjs/swagger';
import { JwtAuthGuard } from '../../auth/guards/jwt-auth.guard';
import { RolesGuard } from '../../auth/guards/roles.guard';
import { Roles } from '../../auth/decorators/roles.decorator';
import { CurrentUser } from '../../auth/decorators/current-user.decorator';
import { UserRole } from '../../auth/enums/user-role.enum';
import { AnalyticsService } from '../services/analytics.service';
import { MetricsService } from '../services/metrics.service';
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

@ApiTags('Analytics')
@ApiBearerAuth('JWT-auth')
@Controller('analytics')
@UseGuards(JwtAuthGuard, RolesGuard)
export class AnalyticsController {
  constructor(
    private readonly analyticsService: AnalyticsService,
    private readonly metricsService: MetricsService,
  ) {}

  @Get('metrics/realtime')
  @ApiOperation({
    summary: 'Get real-time metrics',
    description: 'Retrieve current real-time metrics with 30-second refresh rate',
  })
  @ApiResponse({
    status: 200,
    description: 'Real-time metrics retrieved successfully',
    type: RealtimeMetricsDto,
  })
  @ApiResponse({
    status: 401,
    description: 'Unauthorized - Invalid or missing JWT token',
  })
  @ApiResponse({
    status: 403,
    description: 'Forbidden - Insufficient permissions',
  })
  @Roles(UserRole.USER, UserRole.PREMIUM, UserRole.ENTERPRISE)
  async getRealtimeMetrics(
    @CurrentUser() user: any,
  ): Promise<RealtimeMetricsDto> {
    return this.analyticsService.getRealtimeMetrics(user.sub);
  }

  @Get('metrics/sales/:timeframe')
  @ApiOperation({
    summary: 'Get sales metrics for timeframe',
    description: 'Retrieve sales metrics aggregated by specified timeframe',
  })
  @ApiParam({
    name: 'timeframe',
    description: 'Time period for sales metrics',
    enum: ['hour', 'day', 'week', 'month', 'year'],
    example: 'day',
  })
  @ApiQuery({
    name: 'start',
    description: 'Start date (ISO 8601)',
    required: false,
    example: '2024-01-01T00:00:00Z',
  })
  @ApiQuery({
    name: 'end',
    description: 'End date (ISO 8601)',
    required: false,
    example: '2024-01-31T23:59:59Z',
  })
  @ApiResponse({
    status: 200,
    description: 'Sales metrics retrieved successfully',
    type: SalesMetricsDto,
  })
  @Roles(UserRole.USER, UserRole.PREMIUM, UserRole.ENTERPRISE)
  async getSalesMetrics(
    @Param('timeframe') timeframe: string,
    @Query() query: TimeframeQuery,
    @CurrentUser() user: any,
  ): Promise<SalesMetricsDto> {
    return this.analyticsService.getSalesMetrics(user.sub, timeframe, query);
  }

  @Get('metrics/conversion/:productId?')
  @ApiOperation({
    summary: 'Get conversion rate metrics',
    description: 'Retrieve conversion rates for specific product or overall store',
  })
  @ApiParam({
    name: 'productId',
    description: 'Specific product ID (optional)',
    required: false,
    example: 'prod_123456789',
  })
  @ApiQuery({
    name: 'days',
    description: 'Number of days to analyze (7 or 30)',
    required: false,
    example: 30,
  })
  @ApiResponse({
    status: 200,
    description: 'Conversion metrics retrieved successfully',
    type: ConversionMetricsDto,
  })
  @Roles(UserRole.USER, UserRole.PREMIUM, UserRole.ENTERPRISE)
  async getConversionMetrics(
    @Param('productId') productId: string | undefined,
    @Query() query: MetricsQueryDto,
    @CurrentUser() user: any,
  ): Promise<ConversionMetricsDto> {
    return this.analyticsService.getConversionMetrics(
      user.sub,
      productId,
      query,
    );
  }

  @Get('metrics/engagement')
  @ApiOperation({
    summary: 'Get customer engagement analytics',
    description: 'Retrieve customer engagement patterns and session analytics',
  })
  @ApiQuery({
    name: 'timeframe',
    description: 'Analysis timeframe',
    enum: ['week', 'month', 'quarter'],
    required: false,
    example: 'month',
  })
  @ApiResponse({
    status: 200,
    description: 'Engagement metrics retrieved successfully',
    type: EngagementMetricsDto,
  })
  @Roles(UserRole.USER, UserRole.PREMIUM, UserRole.ENTERPRISE)
  async getEngagementMetrics(
    @Query() query: MetricsQueryDto,
    @CurrentUser() user: any,
  ): Promise<EngagementMetricsDto> {
    return this.analyticsService.getEngagementMetrics(user.sub, query);
  }

  @Get('trends/:metric/:timeframe')
  @ApiOperation({
    summary: 'Get trend analysis for specific metric',
    description: 'Analyze trends for sales, conversion, engagement, or custom metrics',
  })
  @ApiParam({
    name: 'metric',
    description: 'Metric type to analyze',
    enum: ['sales', 'conversion', 'engagement', 'revenue', 'traffic'],
    example: 'sales',
  })
  @ApiParam({
    name: 'timeframe',
    description: 'Analysis timeframe',
    enum: ['week', 'month', 'quarter', 'year'],
    example: 'month',
  })
  @ApiResponse({
    status: 200,
    description: 'Trend analysis completed successfully',
    type: TrendAnalysisDto,
  })
  @Roles(UserRole.PREMIUM, UserRole.ENTERPRISE)
  async getTrendAnalysis(
    @Param('metric') metric: string,
    @Param('timeframe') timeframe: string,
    @Query() query: TimeframeQuery,
    @CurrentUser() user: any,
  ): Promise<TrendAnalysisDto> {
    return this.analyticsService.getTrendAnalysis(
      user.sub,
      metric,
      timeframe,
      query,
    );
  }

  @Get('cohorts/:userId?')
  @ApiOperation({
    summary: 'Get cohort analysis',
    description: 'Analyze customer cohorts and retention patterns',
  })
  @ApiParam({
    name: 'userId',
    description: 'Specific user ID for cohort analysis (optional)',
    required: false,
  })
  @ApiQuery({
    name: 'cohortType',
    description: 'Type of cohort analysis',
    enum: ['acquisition', 'behavioral', 'revenue'],
    required: false,
    example: 'acquisition',
  })
  @ApiResponse({
    status: 200,
    description: 'Cohort analysis completed successfully',
  })
  @Roles(UserRole.PREMIUM, UserRole.ENTERPRISE)
  async getCohortAnalysis(
    @Param('userId', new ParseUUIDPipe({ optional: true })) userId: string,
    @Query() query: any,
    @CurrentUser() user: any,
  ): Promise<any> {
    return this.analyticsService.getCohortAnalysis(
      user.sub,
      userId,
      query.cohortType,
    );
  }

  @Get('funnel/:funnelId')
  @ApiOperation({
    summary: 'Get funnel analysis',
    description: 'Analyze conversion funnels and identify drop-off points',
  })
  @ApiParam({
    name: 'funnelId',
    description: 'Funnel configuration ID',
    example: 'funnel_checkout_flow',
  })
  @ApiResponse({
    status: 200,
    description: 'Funnel analysis completed successfully',
  })
  @Roles(UserRole.PREMIUM, UserRole.ENTERPRISE)
  async getFunnelAnalysis(
    @Param('funnelId') funnelId: string,
    @Query() query: TimeframeQuery,
    @CurrentUser() user: any,
  ): Promise<any> {
    return this.analyticsService.getFunnelAnalysis(user.sub, funnelId, query);
  }

  @Post('query')
  @ApiOperation({
    summary: 'Execute custom analytics query',
    description: 'Run custom queries for advanced analytics and reporting',
  })
  @ApiResponse({
    status: 200,
    description: 'Custom query executed successfully',
  })
  @ApiResponse({
    status: 400,
    description: 'Invalid query parameters',
  })
  @HttpCode(HttpStatus.OK)
  @Roles(UserRole.ENTERPRISE)
  async executeCustomQuery(
    @Body(ValidationPipe) customQuery: CustomQueryDto,
    @CurrentUser() user: any,
  ): Promise<any> {
    return this.analyticsService.executeCustomQuery(user.sub, customQuery);
  }

  @Post('metrics/refresh')
  @ApiOperation({
    summary: 'Refresh metrics cache',
    description: 'Force refresh of cached metrics data',
  })
  @ApiResponse({
    status: 200,
    description: 'Metrics cache refreshed successfully',
  })
  @HttpCode(HttpStatus.OK)
  @Roles(UserRole.PREMIUM, UserRole.ENTERPRISE)
  async refreshMetrics(@CurrentUser() user: any): Promise<{ success: boolean }> {
    await this.metricsService.refreshUserMetrics(user.sub);
    return { success: true };
  }

  @Get('export/:format')
  @ApiOperation({
    summary: 'Export analytics data',
    description: 'Export analytics data in specified format (CSV, Excel, PDF)',
  })
  @ApiParam({
    name: 'format',
    description: 'Export format',
    enum: ['csv', 'excel', 'pdf'],
    example: 'csv',
  })
  @ApiQuery({
    name: 'metrics',
    description: 'Comma-separated list of metrics to export',
    required: false,
    example: 'sales,conversion,engagement',
  })
  @ApiResponse({
    status: 200,
    description: 'Data export initiated successfully',
  })
  @Roles(UserRole.PREMIUM, UserRole.ENTERPRISE)
  async exportData(
    @Param('format') format: string,
    @Query() query: any,
    @CurrentUser() user: any,
  ): Promise<{ exportId: string; downloadUrl?: string }> {
    return this.analyticsService.exportData(user.sub, format, query);
  }
}