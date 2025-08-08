import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Provider } from 'react-redux';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import userEvent from '@testing-library/user-event';

import RealtimeMetricsWidget from './RealtimeMetricsWidget';
import { theme } from '../../styles/theme';
import { analyticsService } from '../../services/analytics';
import { RealtimeMetrics } from '../../types/analytics';

// Mock the analytics service
jest.mock('../../services/analytics');
const mockAnalyticsService = analyticsService as jest.Mocked<typeof analyticsService>;

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock recharts components
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
}));

// Test data
const mockRealtimeData: RealtimeMetrics = {
  timestamp: '2024-01-15T12:00:00Z',
  sales: {
    todayOrders: 25,
    todayRevenue: 2500.00,
    todayItemsSold: 45,
    avgOrderValue: 100.00,
    ordersChange: 15.5,
    revenueChange: 12.3,
  },
  traffic: {
    activeSessions: 8,
    liveVisitors: 8,
  },
  trends: {
    hourlyRevenue: [
      { hour: '2024-01-15T09:00:00Z', revenue: 300 },
      { hour: '2024-01-15T10:00:00Z', revenue: 450 },
      { hour: '2024-01-15T11:00:00Z', revenue: 520 },
      { hour: '2024-01-15T12:00:00Z', revenue: 380 },
    ],
  },
};

// Test utilities
const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

const createTestStore = () =>
  configureStore({
    reducer: {
      auth: (state = { user: { id: 'test-user' } }) => state,
    },
  });

const renderWithProviders = (component: React.ReactElement, options: any = {}) => {
  const queryClient = options.queryClient || createQueryClient();
  const store = options.store || createTestStore();

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <BrowserRouter>
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            {children}
          </ThemeProvider>
        </QueryClientProvider>
      </Provider>
    </BrowserRouter>
  );

  return render(component, { wrapper: Wrapper });
};

describe('RealtimeMetricsWidget', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const defaultProps = {
    widgetId: 'test-widget-1',
    config: {},
    isFullscreen: false,
    onRemove: jest.fn(),
    onSettings: jest.fn(),
    onFullscreen: jest.fn(),
  };

  describe('Rendering', () => {
    it('renders widget with provided realtime data', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={mockRealtimeData}
        />
      );

      expect(screen.getByText('Real-time Metrics')).toBeInTheDocument();
      expect(screen.getByText('LIVE')).toBeInTheDocument();
      expect(screen.getByText('$2,500.00')).toBeInTheDocument(); // Today's Revenue
      expect(screen.getByText('25')).toBeInTheDocument(); // Today's Orders
    });

    it('renders loading state when data is not available', () => {
      mockAnalyticsService.getRealtimeMetrics.mockReturnValue(
        new Promise(() => {}) // Never resolves to simulate loading
      );

      renderWithProviders(
        <RealtimeMetricsWidget {...defaultProps} />
      );

      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('renders error message when data loading fails', async () => {
      mockAnalyticsService.getRealtimeMetrics.mockRejectedValue(
        new Error('API Error')
      );

      renderWithProviders(
        <RealtimeMetricsWidget {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText('No data available')).toBeInTheDocument();
      });
    });

    it('displays metric cards with proper values', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={mockRealtimeData}
        />
      );

      // Revenue card
      expect(screen.getByText("Today's Revenue")).toBeInTheDocument();
      expect(screen.getByText('$2,500.00')).toBeInTheDocument();
      expect(screen.getByText('25 orders')).toBeInTheDocument();

      // Orders card
      expect(screen.getByText('Orders')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
      expect(screen.getByText('45 items')).toBeInTheDocument();

      // Average Order Value card
      expect(screen.getByText('Avg Order Value')).toBeInTheDocument();
      expect(screen.getByText('$100.00')).toBeInTheDocument();

      // Active Visitors card
      expect(screen.getByText('Active Visitors')).toBeInTheDocument();
      expect(screen.getByText('8')).toBeInTheDocument();
      expect(screen.getByText('Live sessions')).toBeInTheDocument();
    });

    it('displays trend indicators correctly', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={mockRealtimeData}
        />
      );

      // Should show positive trends (TrendingUp icons)
      expect(screen.getByText('+15.5%')).toBeInTheDocument();
      expect(screen.getByText('+12.3%')).toBeInTheDocument();
    });

    it('displays negative trends correctly', () => {
      const negativeDataTrends = {
        ...mockRealtimeData,
        sales: {
          ...mockRealtimeData.sales,
          ordersChange: -10.5,
          revenueChange: -5.2,
        },
      };

      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={negativeDataTrends}
        />
      );

      expect(screen.getByText('-10.5%')).toBeInTheDocument();
      expect(screen.getByText('-5.2%')).toBeInTheDocument();
    });
  });

  describe('Chart Functionality', () => {
    it('renders hourly revenue chart', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={mockRealtimeData}
        />
      );

      expect(screen.getByText("Today's Hourly Revenue Trend")).toBeInTheDocument();
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.getByTestId('line')).toBeInTheDocument();
    });

    it('displays chart metadata correctly', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={mockRealtimeData}
        />
      );

      expect(screen.getByText('4 hours of data')).toBeInTheDocument();
      expect(screen.getByText(/Peak hour:/)).toBeInTheDocument();
    });

    it('handles empty chart data gracefully', () => {
      const emptyChartData = {
        ...mockRealtimeData,
        trends: {
          hourlyRevenue: [],
        },
      };

      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={emptyChartData}
        />
      );

      // Chart should not be rendered when no data
      expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('calls onRemove when remove button is clicked', async () => {
      const onRemove = jest.fn();
      
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          onRemove={onRemove}
          realtimeData={mockRealtimeData}
        />
      );

      const removeButton = screen.getByLabelText('Remove Widget');
      await userEvent.click(removeButton);

      expect(onRemove).toHaveBeenCalledTimes(1);
    });

    it('calls onSettings when settings button is clicked', async () => {
      const onSettings = jest.fn();
      
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          onSettings={onSettings}
          realtimeData={mockRealtimeData}
        />
      );

      const settingsButton = screen.getByLabelText('Widget Settings');
      await userEvent.click(settingsButton);

      expect(onSettings).toHaveBeenCalledTimes(1);
    });

    it('calls onFullscreen when fullscreen button is clicked', async () => {
      const onFullscreen = jest.fn();
      
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          onFullscreen={onFullscreen}
          realtimeData={mockRealtimeData}
        />
      );

      const fullscreenButton = screen.getByLabelText('Fullscreen');
      await userEvent.click(fullscreenButton);

      expect(onFullscreen).toHaveBeenCalledTimes(1);
    });

    it('handles manual refresh correctly', async () => {
      mockAnalyticsService.getRealtimeMetrics.mockResolvedValue(mockRealtimeData);

      renderWithProviders(
        <RealtimeMetricsWidget {...defaultProps} />
      );

      const refreshButton = screen.getByLabelText('Refresh Data');
      await userEvent.click(refreshButton);

      expect(mockAnalyticsService.getRealtimeMetrics).toHaveBeenCalled();
    });

    it('disables refresh button during refresh', async () => {
      mockAnalyticsService.getRealtimeMetrics.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockRealtimeData), 100))
      );

      renderWithProviders(
        <RealtimeMetricsWidget {...defaultProps} />
      );

      const refreshButton = screen.getByLabelText('Refresh Data');
      await userEvent.click(refreshButton);

      expect(refreshButton).toBeDisabled();
    });
  });

  describe('Fullscreen Mode', () => {
    it('renders in fullscreen mode correctly', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          isFullscreen={true}
          realtimeData={mockRealtimeData}
        />
      );

      // Check for fullscreen classes
      expect(screen.getByRole('region')).toHaveClass('fixed', 'inset-0', 'z-50');
      
      // Remove button should not be visible in fullscreen
      expect(screen.queryByLabelText('Remove Widget')).not.toBeInTheDocument();
    });

    it('displays exit fullscreen button in fullscreen mode', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          isFullscreen={true}
          realtimeData={mockRealtimeData}
        />
      );

      expect(screen.getByLabelText('Exit Fullscreen')).toBeInTheDocument();
    });
  });

  describe('Performance Indicators', () => {
    it('displays performance status cards', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={mockRealtimeData}
        />
      );

      expect(screen.getByText('Growing')).toBeInTheDocument();
      expect(screen.getByText('8 Active')).toBeInTheDocument();
      expect(screen.getByText('Real-time')).toBeInTheDocument();
    });

    it('shows stable status for zero change', () => {
      const stableData = {
        ...mockRealtimeData,
        sales: {
          ...mockRealtimeData.sales,
          revenueChange: 0,
        },
      };

      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={stableData}
        />
      );

      expect(screen.getByText('Stable')).toBeInTheDocument();
    });
  });

  describe('Data Updates', () => {
    it('updates last update time when data changes', () => {
      const { rerender } = renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={mockRealtimeData}
        />
      );

      const firstUpdateText = screen.getByText(/Last updated:/);
      
      // Update with new data
      const newData = {
        ...mockRealtimeData,
        timestamp: '2024-01-15T12:30:00Z',
        sales: {
          ...mockRealtimeData.sales,
          todayOrders: 30,
        },
      };

      rerender(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={newData}
        />
      );

      expect(screen.getByText('30')).toBeInTheDocument(); // Updated orders count
    });
  });

  describe('Accessibility', () => {
    it('provides proper ARIA labels for buttons', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={mockRealtimeData}
        />
      );

      expect(screen.getByLabelText('Refresh Data')).toBeInTheDocument();
      expect(screen.getByLabelText('Widget Settings')).toBeInTheDocument();
      expect(screen.getByLabelText('Fullscreen')).toBeInTheDocument();
      expect(screen.getByLabelText('Remove Widget')).toBeInTheDocument();
    });

    it('maintains keyboard navigation', async () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={mockRealtimeData}
        />
      );

      const refreshButton = screen.getByLabelText('Refresh Data');
      refreshButton.focus();
      expect(document.activeElement).toBe(refreshButton);

      // Tab to next button
      await userEvent.tab();
      expect(document.activeElement).toBe(screen.getByLabelText('Widget Settings'));
    });
  });

  describe('Error Handling', () => {
    it('handles network errors gracefully', async () => {
      mockAnalyticsService.getRealtimeMetrics.mockRejectedValue(
        new Error('Network Error')
      );

      renderWithProviders(
        <RealtimeMetricsWidget {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText('No data available')).toBeInTheDocument();
      });
    });

    it('handles malformed data gracefully', () => {
      const malformedData = {
        ...mockRealtimeData,
        sales: {
          ...mockRealtimeData.sales,
          todayRevenue: null, // Invalid value
        },
      };

      // Should not crash
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          realtimeData={malformedData as any}
        />
      );

      expect(screen.getByText('Real-time Metrics')).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    it('adjusts layout for fullscreen mode', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          isFullscreen={true}
          realtimeData={mockRealtimeData}
        />
      );

      // In fullscreen, chart should be taller
      const chartContainer = screen.getByTestId('responsive-container');
      expect(chartContainer.parentElement).toHaveClass('h-96');
    });

    it('displays compact layout for normal mode', () => {
      renderWithProviders(
        <RealtimeMetricsWidget
          {...defaultProps}
          isFullscreen={false}
          realtimeData={mockRealtimeData}
        />
      );

      // In normal mode, chart should be shorter
      const chartContainer = screen.getByTestId('responsive-container');
      expect(chartContainer.parentElement).toHaveClass('h-48');
    });
  });
});