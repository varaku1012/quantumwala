import React, { useState, useCallback, useMemo } from 'react';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import { Grid, IconButton, Typography, Box, Fab, Tooltip } from '@mui/material';
import {
  Settings as SettingsIcon,
  Add as AddIcon,
  Fullscreen as FullscreenIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

// Components
import { DashboardGrid } from '../../components/Dashboard/DashboardGrid';
import { WidgetSelector } from '../../components/Dashboard/WidgetSelector';
import { DashboardSettings } from '../../components/Dashboard/DashboardSettings';
import { LoadingSpinner } from '../../components/UI/LoadingSpinner';
import { ErrorMessage } from '../../components/UI/ErrorMessage';

// Widgets
import { RealtimeMetricsWidget } from '../../components/Widgets/RealtimeMetricsWidget';
import { SalesChartWidget } from '../../components/Widgets/SalesChartWidget';
import { ConversionRateWidget } from '../../components/Widgets/ConversionRateWidget';
import { EngagementWidget } from '../../components/Widgets/EngagementWidget';
import { RevenueForecastWidget } from '../../components/Widgets/RevenueForecastWidget';
import { TopProductsWidget } from '../../components/Widgets/TopProductsWidget';
import { AlertsWidget } from '../../components/Widgets/AlertsWidget';
import { MarketTrendsWidget } from '../../components/Widgets/MarketTrendsWidget';

// Hooks
import { useDashboard } from '../../hooks/useDashboard';
import { useRealtimeUpdates } from '../../hooks/useRealtimeUpdates';
import { useAuth } from '../../hooks/useAuth';

// Types
import { WidgetConfig, DashboardLayout } from '../../types/dashboard';
import { RealtimeMetrics } from '../../types/analytics';

// Services
import { analyticsService } from '../../services/analytics';
import { dashboardService } from '../../services/dashboard';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const {
    dashboardConfig,
    updateLayout,
    addWidget,
    removeWidget,
    updateWidget,
    isLoading: dashboardLoading,
  } = useDashboard();

  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isWidgetSelectorOpen, setIsWidgetSelectorOpen] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState<string | null>(null);
  const [fullscreenWidget, setFullscreenWidget] = useState<string | null>(null);

  // Real-time metrics query
  const {
    data: realtimeMetrics,
    isLoading: metricsLoading,
    error: metricsError,
    refetch: refetchMetrics,
  } = useQuery<RealtimeMetrics>({
    queryKey: ['realtime-metrics', user?.id],
    queryFn: () => analyticsService.getRealtimeMetrics(),
    enabled: !!user,
    refetchInterval: 30000, // 30 seconds
    staleTime: 25000, // 25 seconds
  });

  // WebSocket real-time updates
  useRealtimeUpdates({
    onMetricsUpdate: (data) => {
      // Invalidate and refetch metrics when real-time update received
      refetchMetrics();
    },
    onAlert: (alert) => {
      toast.error(alert.message, {
        duration: 6000,
        icon: '🚨',
      });
    },
  });

  // Widget configuration map
  const widgetComponents = useMemo(() => ({
    'realtime-metrics': RealtimeMetricsWidget,
    'sales-chart': SalesChartWidget,
    'conversion-rate': ConversionRateWidget,
    'engagement': EngagementWidget,
    'revenue-forecast': RevenueForecastWidget,
    'top-products': TopProductsWidget,
    'alerts': AlertsWidget,
    'market-trends': MarketTrendsWidget,
  }), []);

  // Handle layout changes from drag-and-drop
  const handleLayoutChange = useCallback((layout: DashboardLayout[]) => {
    updateLayout(layout);
  }, [updateLayout]);

  // Handle adding new widget
  const handleAddWidget = useCallback((widgetType: string) => {
    const newWidget: WidgetConfig = {
      id: `${widgetType}-${Date.now()}`,
      type: widgetType,
      title: getWidgetTitle(widgetType),
      position: { x: 0, y: 0, w: 4, h: 3 },
      config: {},
    };
    addWidget(newWidget);
    setIsWidgetSelectorOpen(false);
    toast.success('Widget added successfully');
  }, [addWidget]);

  // Handle removing widget
  const handleRemoveWidget = useCallback((widgetId: string) => {
    removeWidget(widgetId);
    toast.success('Widget removed');
  }, [removeWidget]);

  // Handle widget settings update
  const handleUpdateWidget = useCallback((widgetId: string, updates: Partial<WidgetConfig>) => {
    updateWidget(widgetId, updates);
    toast.success('Widget updated');
  }, [updateWidget]);

  // Handle manual metrics refresh
  const handleRefresh = useCallback(async () => {
    try {
      await refetchMetrics();
      toast.success('Dashboard refreshed');
    } catch (error) {
      toast.error('Failed to refresh dashboard');
    }
  }, [refetchMetrics]);

  // Handle fullscreen toggle
  const handleToggleFullscreen = useCallback((widgetId: string | null) => {
    setFullscreenWidget(widgetId);
  }, []);

  // Render individual widget
  const renderWidget = useCallback((widget: WidgetConfig) => {
    const WidgetComponent = widgetComponents[widget.type as keyof typeof widgetComponents];
    
    if (!WidgetComponent) {
      return (
        <ErrorMessage 
          message={`Unknown widget type: ${widget.type}`}
          action={{
            label: 'Remove Widget',
            onClick: () => handleRemoveWidget(widget.id),
          }}
        />
      );
    }

    return (
      <WidgetComponent
        key={widget.id}
        widgetId={widget.id}
        config={widget.config}
        isFullscreen={fullscreenWidget === widget.id}
        onRemove={() => handleRemoveWidget(widget.id)}
        onSettings={() => setSelectedWidget(widget.id)}
        onFullscreen={() => handleToggleFullscreen(
          fullscreenWidget === widget.id ? null : widget.id
        )}
        realtimeData={realtimeMetrics}
      />
    );
  }, [
    widgetComponents,
    fullscreenWidget,
    realtimeMetrics,
    handleRemoveWidget,
    handleToggleFullscreen,
  ]);

  if (dashboardLoading) {
    return <LoadingSpinner message=\"Loading dashboard...\" />;
  }

  if (metricsError) {
    return (
      <ErrorMessage
        message=\"Failed to load dashboard data\"
        action={{
          label: 'Retry',
          onClick: handleRefresh,
        }}
      />
    );
  }

  return (
    <>
      <Helmet>
        <title>Analytics Dashboard - EtsyPro AI</title>
        <meta name=\"description\" content=\"Real-time analytics dashboard for Etsy sellers\" />
      </Helmet>

      <div className=\"dashboard-container h-full\">
        {/* Dashboard Header */}
        <Box className=\"dashboard-header flex items-center justify-between p-4 bg-white shadow-sm border-b\">
          <div className=\"flex items-center space-x-4\">
            <Typography variant=\"h4\" className=\"font-bold text-gray-900\">
              Analytics Dashboard
            </Typography>
            
            {metricsLoading && (
              <div className=\"flex items-center space-x-2 text-blue-600\">
                <div className=\"animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent\" />
                <Typography variant=\"caption\">Updating...</Typography>
              </div>
            )}
          </div>

          <div className=\"flex items-center space-x-2\">
            <Tooltip title=\"Refresh Dashboard\">
              <IconButton onClick={handleRefresh} disabled={metricsLoading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title=\"Dashboard Settings\">
              <IconButton onClick={() => setIsSettingsOpen(true)}>
                <SettingsIcon />
              </IconButton>
            </Tooltip>

            {fullscreenWidget && (
              <Tooltip title=\"Exit Fullscreen\">
                <IconButton onClick={() => handleToggleFullscreen(null)}>
                  <FullscreenIcon />
                </IconButton>
              </Tooltip>
            )}
          </div>
        </Box>

        {/* Dashboard Content */}
        <div className=\"dashboard-content p-4 h-full overflow-auto\">
          {fullscreenWidget ? (
            // Fullscreen widget view
            <div className=\"h-full\">
              {dashboardConfig.widgets
                .filter(widget => widget.id === fullscreenWidget)
                .map(renderWidget)}
            </div>
          ) : (
            // Normal grid view
            <DashboardGrid
              widgets={dashboardConfig.widgets}
              layout={dashboardConfig.layout}
              onLayoutChange={handleLayoutChange}
              renderWidget={renderWidget}
              isDraggable={true}
              isResizable={true}
            />
          )}

          {/* Empty state */}
          {dashboardConfig.widgets.length === 0 && (
            <div className=\"flex flex-col items-center justify-center h-96 text-gray-500\">
              <Typography variant=\"h6\" className=\"mb-4\">
                Your dashboard is empty
              </Typography>
              <Typography variant=\"body2\" className=\"mb-8 text-center max-w-md\">
                Add widgets to start tracking your analytics and business metrics.
              </Typography>
              <button
                onClick={() => setIsWidgetSelectorOpen(true)}
                className=\"px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors\"
              >
                Add Your First Widget
              </button>
            </div>
          )}
        </div>

        {/* Floating Add Button */}
        {dashboardConfig.widgets.length > 0 && !fullscreenWidget && (
          <Fab
            color=\"primary\"
            className=\"fixed bottom-6 right-6 z-50\"
            onClick={() => setIsWidgetSelectorOpen(true)}
          >
            <AddIcon />
          </Fab>
        )}

        {/* Widget Selector Modal */}
        <WidgetSelector
          open={isWidgetSelectorOpen}
          onClose={() => setIsWidgetSelectorOpen(false)}
          onSelectWidget={handleAddWidget}
          availableWidgets={Object.keys(widgetComponents)}
          existingWidgets={dashboardConfig.widgets}
        />

        {/* Dashboard Settings Modal */}
        <DashboardSettings
          open={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          dashboardConfig={dashboardConfig}
          onUpdateConfig={(config) => {
            // Update dashboard configuration
            dashboardService.updateDashboard(config);
            toast.success('Dashboard settings updated');
          }}
        />
      </div>
    </>
  );
};

// Helper function to get widget titles
const getWidgetTitle = (widgetType: string): string => {
  const titles: Record<string, string> = {
    'realtime-metrics': 'Real-time Metrics',
    'sales-chart': 'Sales Chart',
    'conversion-rate': 'Conversion Rate',
    'engagement': 'Customer Engagement',
    'revenue-forecast': 'Revenue Forecast',
    'top-products': 'Top Products',
    'alerts': 'Alerts & Notifications',
    'market-trends': 'Market Trends',
  };
  return titles[widgetType] || 'Unknown Widget';
};

export default Dashboard;