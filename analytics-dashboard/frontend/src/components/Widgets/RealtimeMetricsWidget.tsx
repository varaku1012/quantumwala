import React, { useState, useEffect, useMemo } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Box,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  AttachMoney,
  ShoppingCart,
  Visibility,
  People,
  Refresh,
  Settings,
  Fullscreen,
  Close,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

// Types
import { RealtimeMetrics } from '../../types/analytics';
import { WidgetProps } from '../../types/widgets';

// Hooks
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../../services/analytics';

// Utils
import { formatCurrency, formatNumber, formatPercentage } from '../../utils/formatters';

interface RealtimeMetricsWidgetProps extends WidgetProps {
  realtimeData?: RealtimeMetrics;
}

const RealtimeMetricsWidget: React.FC<RealtimeMetricsWidgetProps> = ({
  widgetId,
  config,
  isFullscreen,
  onRemove,
  onSettings,
  onFullscreen,
  realtimeData,
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdateTime, setLastUpdateTime] = useState<Date>(new Date());

  // Fallback query if realtime data is not provided
  const { 
    data: fallbackData, 
    isLoading,
    refetch: refetchData 
  } = useQuery<RealtimeMetrics>({
    queryKey: ['realtime-metrics-widget', widgetId],
    queryFn: () => analyticsService.getRealtimeMetrics(),
    enabled: !realtimeData,
    refetchInterval: 30000, // 30 seconds
  });

  const metrics = realtimeData || fallbackData;

  // Update last update time when data changes
  useEffect(() => {
    if (metrics) {
      setLastUpdateTime(new Date());
    }
  }, [metrics]);

  // Handle manual refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refetchData();
    } finally {
      setIsRefreshing(false);
    }
  };

  // Memoized metric cards data
  const metricCards = useMemo(() => {
    if (!metrics) return [];

    return [
      {
        title: 'Today\'s Revenue',
        value: formatCurrency(metrics.sales.todayRevenue),
        change: metrics.sales.revenueChange,
        icon: AttachMoney,
        color: 'success' as const,
        subtitle: `${formatNumber(metrics.sales.todayOrders)} orders`,
      },
      {
        title: 'Orders',
        value: formatNumber(metrics.sales.todayOrders),
        change: metrics.sales.ordersChange,
        icon: ShoppingCart,
        color: 'primary' as const,
        subtitle: `${formatNumber(metrics.sales.todayItemsSold)} items`,
      },
      {
        title: 'Avg Order Value',
        value: formatCurrency(metrics.sales.avgOrderValue),
        change: 0, // Would calculate from historical data
        icon: AttachMoney,
        color: 'info' as const,
        subtitle: 'Per order',
      },
      {
        title: 'Active Visitors',
        value: formatNumber(metrics.traffic.activeSessions),
        change: 0, // Would calculate from historical data
        icon: People,
        color: 'warning' as const,
        subtitle: 'Live sessions',
      },
    ];
  }, [metrics]);

  // Chart data for hourly trends
  const chartData = useMemo(() => {
    if (!metrics?.trends.hourlyRevenue) return [];
    
    return metrics.trends.hourlyRevenue.map(point => ({
      hour: new Date(point.hour).toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        hour12: true 
      }),
      revenue: point.revenue,
      timestamp: point.hour,
    }));
  }, [metrics]);

  const renderTrendIcon = (change: number, size: 'small' | 'medium' = 'small') => {
    if (change > 0) {
      return <TrendingUp color=\"success\" fontSize={size} />;
    } else if (change < 0) {
      return <TrendingDown color=\"error\" fontSize={size} />;
    } else {
      return <TrendingFlat color=\"disabled\" fontSize={size} />;
    }
  };

  const renderMetricCard = (metric: typeof metricCards[0], index: number) => (
    <Grid item xs={12} sm={6} lg={isFullscreen ? 3 : 6} key={metric.title}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.1 }}
      >
        <Card className=\"h-full bg-gradient-to-r from-white to-gray-50 hover:shadow-lg transition-shadow\">
          <CardContent className=\"p-4\">
            <Box className=\"flex items-start justify-between mb-3\">
              <metric.icon 
                className={`text-${metric.color === 'success' ? 'green' : 
                            metric.color === 'error' ? 'red' :
                            metric.color === 'warning' ? 'orange' : 'blue'}-500`}
                fontSize=\"large\"
              />
              <div className=\"flex items-center space-x-1\">
                {renderTrendIcon(metric.change)}
                <Typography 
                  variant=\"caption\" 
                  className={`font-semibold ${
                    metric.change > 0 ? 'text-green-600' :
                    metric.change < 0 ? 'text-red-600' : 'text-gray-500'
                  }`}
                >
                  {metric.change !== 0 ? formatPercentage(metric.change) : '--'}
                </Typography>
              </div>
            </Box>
            
            <Typography variant=\"h4\" className=\"font-bold mb-1 text-gray-900\">
              {metric.value}
            </Typography>
            
            <Typography variant=\"body2\" color=\"textSecondary\" className=\"mb-2\">
              {metric.title}
            </Typography>
            
            <Typography variant=\"caption\" color=\"textSecondary\">
              {metric.subtitle}
            </Typography>
          </CardContent>
        </Card>
      </motion.div>
    </Grid>
  );

  if (isLoading) {
    return (
      <Card className=\"h-full\">
        <CardContent className=\"flex items-center justify-center h-full\">
          <CircularProgress />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`h-full ${isFullscreen ? 'fixed inset-0 z-50 rounded-none' : ''}`}>
      <div className=\"flex items-center justify-between p-4 border-b bg-gray-50\">
        <div className=\"flex items-center space-x-3\">
          <Typography variant=\"h6\" className=\"font-semibold\">
            Real-time Metrics
          </Typography>
          <Chip 
            label=\"LIVE\" 
            size=\"small\" 
            className=\"bg-green-100 text-green-800 animate-pulse\" 
          />
          <Typography variant=\"caption\" color=\"textSecondary\">
            Last updated: {lastUpdateTime.toLocaleTimeString()}
          </Typography>
        </div>
        
        <div className=\"flex items-center space-x-1\">
          <Tooltip title=\"Refresh Data\">
            <IconButton 
              onClick={handleRefresh} 
              disabled={isRefreshing}
              size=\"small\"
            >
              {isRefreshing ? (
                <CircularProgress size={20} />
              ) : (
                <Refresh className={isRefreshing ? 'animate-spin' : ''} />
              )}
            </IconButton>
          </Tooltip>
          
          {onSettings && (
            <Tooltip title=\"Widget Settings\">
              <IconButton onClick={onSettings} size=\"small\">
                <Settings />
              </IconButton>
            </Tooltip>
          )}
          
          {onFullscreen && (
            <Tooltip title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}>
              <IconButton onClick={onFullscreen} size=\"small\">
                <Fullscreen />
              </IconButton>
            </Tooltip>
          )}
          
          {onRemove && !isFullscreen && (
            <Tooltip title=\"Remove Widget\">
              <IconButton onClick={onRemove} size=\"small\">
                <Close />
              </IconButton>
            </Tooltip>
          )}
        </div>
      </div>

      <CardContent className={`p-4 ${isFullscreen ? 'h-[calc(100%-80px)] overflow-auto' : ''}`}>
        <AnimatePresence mode=\"wait\">
          {metrics ? (
            <motion.div
              key=\"metrics-content\"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className=\"space-y-6\"
            >
              {/* Metric Cards Grid */}
              <Grid container spacing={3}>
                {metricCards.map(renderMetricCard)}
              </Grid>

              {/* Hourly Revenue Trend Chart */}
              {chartData.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <Card className=\"bg-gradient-to-r from-blue-50 to-purple-50\">
                    <CardContent className=\"p-4\">
                      <Typography variant=\"h6\" className=\"mb-4 font-semibold\">
                        Today's Hourly Revenue Trend
                      </Typography>
                      
                      <div className={isFullscreen ? 'h-96' : 'h-48'}>
                        <ResponsiveContainer width=\"100%\" height=\"100%\">
                          <LineChart data={chartData}>
                            <XAxis 
                              dataKey=\"hour\" 
                              tick={{ fontSize: 12 }}
                              tickLine={false}
                            />
                            <YAxis 
                              tick={{ fontSize: 12 }}
                              tickLine={false}
                              axisLine={false}
                              tickFormatter={(value) => formatCurrency(value, { compact: true })}
                            />
                            <RechartsTooltip 
                              formatter={(value: number) => [formatCurrency(value), 'Revenue']}
                              labelStyle={{ color: '#374151' }}
                              contentStyle={{
                                backgroundColor: '#f9fafb',
                                border: '1px solid #e5e7eb',
                                borderRadius: '8px',
                              }}
                            />
                            <Line 
                              type=\"monotone\" 
                              dataKey=\"revenue\" 
                              stroke=\"#3b82f6\" 
                              strokeWidth={3}
                              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                              activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                      
                      {chartData.length > 0 && (
                        <div className=\"mt-4 flex items-center justify-between text-sm text-gray-600\">
                          <span>Peak hour: {
                            chartData.reduce((max, curr) => 
                              curr.revenue > max.revenue ? curr : max
                            ).hour
                          }</span>
                          <span>{chartData.length} hours of data</span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              {/* Performance Indicators */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className=\"grid grid-cols-1 md:grid-cols-3 gap-4\"
              >
                <Card className=\"bg-gradient-to-r from-green-50 to-emerald-50\">
                  <CardContent className=\"p-4 text-center\">
                    <TrendingUp className=\"text-green-500 mb-2\" fontSize=\"large\" />
                    <Typography variant=\"h6\" className=\"font-bold text-green-700\">
                      {metrics.sales.revenueChange > 0 ? 'Growing' : 'Stable'}
                    </Typography>
                    <Typography variant=\"body2\" color=\"textSecondary\">
                      Revenue trend vs yesterday
                    </Typography>
                  </CardContent>
                </Card>

                <Card className=\"bg-gradient-to-r from-blue-50 to-cyan-50\">
                  <CardContent className=\"p-4 text-center\">
                    <People className=\"text-blue-500 mb-2\" fontSize=\"large\" />
                    <Typography variant=\"h6\" className=\"font-bold text-blue-700\">
                      {metrics.traffic.activeSessions} Active
                    </Typography>
                    <Typography variant=\"body2\" color=\"textSecondary\">
                      Live visitors right now
                    </Typography>
                  </CardContent>
                </Card>

                <Card className=\"bg-gradient-to-r from-purple-50 to-pink-50\">
                  <CardContent className=\"p-4 text-center\">
                    <Visibility className=\"text-purple-500 mb-2\" fontSize=\"large\" />
                    <Typography variant=\"h6\" className=\"font-bold text-purple-700\">
                      Real-time
                    </Typography>
                    <Typography variant=\"body2\" color=\"textSecondary\">
                      Updates every 30 seconds
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          ) : (
            <motion.div
              key=\"no-data\"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className=\"flex flex-col items-center justify-center h-48 text-gray-500\"
            >
              <Typography variant=\"h6\" className=\"mb-2\">
                No data available
              </Typography>
              <Typography variant=\"body2\" className=\"text-center\">
                Real-time metrics will appear here once data is available.
              </Typography>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
};

export default RealtimeMetricsWidget;