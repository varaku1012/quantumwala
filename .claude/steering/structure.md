# Structure Steering Document - EtsyPro AI

**Version:** 1.0.0  
**Last Updated:** 2025-08-04  
**Platform:** EtsyPro AI - Intelligent Revenue Optimization Platform

## Directory Organization

### Project Root Structure
```
etsypro-ai/
├── apps/                   # Application packages
│   ├── web/               # React web application
│   ├── mobile/            # React Native mobile app
│   └── api/               # Backend API services
├── packages/              # Shared packages
│   ├── ui/                # Shared UI components
│   ├── utils/             # Utility functions
│   ├── types/             # TypeScript type definitions
│   └── config/            # Shared configuration
├── services/              # Microservices
│   ├── auth/              # Authentication service
│   ├── analytics/         # Analytics service
│   ├── ml/                # Machine learning service
│   ├── automation/        # Automation service
│   └── notification/      # Notification service
├── infrastructure/        # Infrastructure as code
│   ├── terraform/         # Terraform configurations
│   ├── kubernetes/        # K8s manifests
│   └── docker/            # Docker configurations
├── scripts/               # Build and deployment scripts
├── docs/                  # Documentation
└── .claude/               # Claude Code agent system
```

### Frontend Application Structure
```
apps/web/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── common/        # Generic components
│   │   ├── forms/         # Form components
│   │   └── charts/        # Chart components
│   ├── pages/             # Page components
│   │   ├── dashboard/     # Dashboard pages
│   │   ├── analytics/     # Analytics pages
│   │   ├── automation/    # Automation pages
│   │   └── settings/      # Settings pages
│   ├── hooks/             # React hooks
│   ├── services/          # API service layer
│   ├── store/             # Redux store
│   │   ├── slices/        # Redux slices
│   │   └── api/           # RTK Query APIs
│   ├── utils/             # Utility functions
│   ├── types/             # TypeScript types
│   └── assets/            # Static assets
├── public/                # Public static files
└── tests/                 # Test files
```

### Backend Service Structure
```
services/analytics/
├── src/
│   ├── controllers/       # HTTP controllers
│   ├── services/          # Business logic
│   ├── repositories/      # Data access layer
│   ├── models/            # Data models
│   ├── middleware/        # Express middleware
│   ├── utils/             # Utility functions
│   ├── types/             # TypeScript types
│   └── config/            # Configuration
├── tests/                 # Test files
├── migrations/            # Database migrations
└── docker/                # Docker files
```

### Machine Learning Service Structure
```
services/ml/
├── src/
│   ├── models/            # ML model definitions
│   ├── training/          # Training scripts
│   ├── inference/         # Inference endpoints
│   ├── preprocessing/     # Data preprocessing
│   ├── evaluation/        # Model evaluation
│   └── utils/             # ML utilities
├── data/                  # Training data
├── notebooks/             # Jupyter notebooks
├── experiments/           # Experiment tracking
└── models/                # Trained model artifacts
```

## Naming Conventions

### Files and Directories
- **Components**: PascalCase.tsx (e.g., DashboardChart.tsx)
- **Pages**: PascalCase.tsx (e.g., AnalyticsDashboard.tsx)
- **Hooks**: camelCase.ts starting with 'use' (e.g., useEtsyData.ts)
- **Services**: camelCase.ts (e.g., analyticsService.ts)
- **Utils**: camelCase.ts (e.g., formatCurrency.ts)
- **Types**: PascalCase.ts (e.g., SellerProfile.ts)
- **Tests**: *.test.ts or *.spec.ts

### Code Elements
- **Components**: PascalCase (e.g., DashboardChart)
- **Functions**: camelCase (e.g., fetchSellerData)
- **Variables**: camelCase (e.g., sellerRevenue)
- **Constants**: UPPER_SNAKE_CASE (e.g., MAX_RETRY_ATTEMPTS)
- **Interfaces**: PascalCase with 'I' prefix (e.g., ISellerData)
- **Types**: PascalCase (e.g., SellerMetrics)
- **Enums**: PascalCase (e.g., SubscriptionTier)

### Database
- **Tables**: snake_case plural (e.g., seller_profiles, product_listings)
- **Columns**: snake_case (e.g., created_at, seller_id)
- **Indexes**: idx_table_column (e.g., idx_sellers_email)
- **Foreign Keys**: fk_table_reference (e.g., fk_listings_seller)

### API Endpoints
- **REST Resources**: kebab-case plural (e.g., /api/v1/seller-profiles)
- **Query Parameters**: camelCase (e.g., ?sortBy=revenue&orderBy=desc)
- **Path Parameters**: camelCase (e.g., /sellers/:sellerId/listings)

## Code Organization Patterns

### Component Structure
```
DashboardChart/
├── index.ts              # Public exports
├── DashboardChart.tsx    # Main component
├── DashboardChart.test.tsx # Tests
├── DashboardChart.styles.ts # Styled components
├── hooks.ts              # Component-specific hooks
└── types.ts              # Component types
```

### Service Layer Pattern
```typescript
// analyticsService.ts
export class AnalyticsService {
  async getSellerMetrics(sellerId: string): Promise<SellerMetrics> {
    // Implementation
  }
  
  async getRevenueForecasting(params: ForecastParams): Promise<RevenueForcast> {
    // Implementation
  }
}
```

### Import Order
1. React and React-related imports
2. Third-party library imports (alphabetical)
3. Internal package imports
4. Component/service imports
5. Type imports (with 'type' prefix)
6. Relative imports

### Module Exports
- Use named exports for utilities and services
- Use default exports for React components
- Export types and interfaces separately

## API Design Patterns

### REST API Structure
```
/api/v1/
├── /auth                  # Authentication endpoints
├── /sellers               # Seller management
├── /products              # Product management  
├── /analytics             # Analytics data
├── /automation            # Automation rules
├── /subscriptions         # Subscription management
└── /integrations          # Third-party integrations
```

### Response Format
```typescript
interface ApiResponse<T> {
  data: T;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
  };
  links?: {
    self: string;
    next?: string;
    prev?: string;
  };
}

interface ApiError {
  error: {
    code: string;
    message: string;
    details?: any;
  };
}
```

### GraphQL Schema Organization
```
schema/
├── types/                 # GraphQL type definitions
├── resolvers/             # Resolver functions
├── mutations/             # Mutation definitions
├── queries/               # Query definitions
└── subscriptions/         # Subscription definitions
```

## Testing Structure

### Test Organization
- **Unit Tests**: Colocated with source files (*.test.ts)
- **Integration Tests**: `/tests/integration/`
- **E2E Tests**: `/tests/e2e/`
- **API Tests**: `/tests/api/`

### Test Naming Conventions
```typescript
describe('AnalyticsService', () => {
  describe('getSellerMetrics', () => {
    it('should return metrics for valid seller ID', () => {
      // Test implementation
    });
    
    it('should throw error for invalid seller ID', () => {
      // Test implementation
    });
  });
});
```

### Mock Organization
```
tests/
├── __mocks__/             # Jest mocks
├── fixtures/              # Test data fixtures
└── helpers/               # Test helper functions
```

## Configuration Management

### Environment Variables
```typescript
// Environment variable naming
REACT_APP_API_URL=http://localhost:3000/api/v1
REACT_APP_ETSY_CLIENT_ID=your_etsy_client_id
NODE_ENV=development
DATABASE_URL=postgresql://localhost:5432/etsypro
REDIS_URL=redis://localhost:6379
```

### Config Structure
```typescript
// config/index.ts
export const config = {
  api: {
    baseUrl: process.env.REACT_APP_API_URL,
    timeout: 30000,
  },
  etsy: {
    clientId: process.env.REACT_APP_ETSY_CLIENT_ID,
    apiVersion: 'v3',
  },
  features: {
    enableBetaFeatures: process.env.NODE_ENV === 'development',
    enableAnalytics: true,
  },
};
```

## Data Flow Patterns

### State Management
```typescript
// Redux store structure
{
  auth: AuthState,
  sellers: SellersState,
  analytics: AnalyticsState,
  automation: AutomationState,
  ui: UIState
}
```

### API Data Flow
```
Component → Hook → Service → API → Database
                ↓
             Redux Store
```

### Error Handling Pattern
```typescript
// Error handling structure
export class AppError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number = 500
  ) {
    super(message);
  }
}

// Error types
export const ErrorCodes = {
  ETSY_API_ERROR: 'ETSY_API_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
} as const;
```

## Documentation Standards

### Code Documentation
```typescript
/**
 * Calculates revenue optimization suggestions for a seller
 * @param sellerId - The unique identifier for the seller
 * @param timeframe - The time period for analysis (30d, 90d, 1y)
 * @returns Promise containing optimization suggestions
 * @throws {AppError} When seller is not found or API fails
 */
async function getOptimizationSuggestions(
  sellerId: string,
  timeframe: TimeFrame
): Promise<OptimizationSuggestions> {
  // Implementation
}
```

### Component Documentation
```typescript
interface DashboardChartProps {
  /** The data to display in the chart */
  data: ChartData[];
  /** Chart type - line, bar, or pie */
  type: 'line' | 'bar' | 'pie';
  /** Optional title for the chart */
  title?: string;
  /** Callback fired when chart is clicked */
  onChartClick?: (dataPoint: ChartDataPoint) => void;
}

/**
 * A reusable chart component for displaying seller analytics data
 * 
 * @example
 * <DashboardChart 
 *   data={revenueData} 
 *   type="line" 
 *   title="Revenue Trend" 
 * />
 */
export const DashboardChart: React.FC<DashboardChartProps> = ({
  data,
  type,
  title,
  onChartClick
}) => {
  // Component implementation
};
```

## Performance Guidelines

### Bundle Size Limits
- **Initial Bundle**: <500KB gzipped
- **Route Chunks**: <200KB gzipped
- **Vendor Bundle**: <300KB gzipped

### Code Splitting Strategy
```typescript
// Route-based splitting
const AnalyticsDashboard = lazy(() => import('./pages/AnalyticsDashboard'));
const AutomationCenter = lazy(() => import('./pages/AutomationCenter'));

// Component-based splitting for heavy components
const AdvancedChart = lazy(() => import('./components/AdvancedChart'));
```

### Image Optimization
- Use WebP format with fallbacks
- Implement lazy loading for images
- Provide multiple sizes for responsive images
- Compress images to <100KB where possible

---
*Last Updated: 2025-08-04*
*Lead Developer: EtsyPro AI Team*