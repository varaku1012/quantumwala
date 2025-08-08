import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { HelmetProvider } from 'react-helmet-async';
import { Toaster } from 'react-hot-toast';

// Store and Theme
import { store } from './store/store';
import { theme } from './styles/theme';

// Components
import { Layout } from './components/Layout/Layout';
import { LoadingSpinner } from './components/UI/LoadingSpinner';
import { ErrorBoundary } from './components/ErrorBoundary/ErrorBoundary';
import { AuthProvider } from './providers/AuthProvider';
import { WebSocketProvider } from './providers/WebSocketProvider';
import { ProtectedRoute } from './components/Auth/ProtectedRoute';

// Pages (Lazy loaded)
const Dashboard = React.lazy(() => import('./pages/Dashboard/Dashboard'));
const Analytics = React.lazy(() => import('./pages/Analytics/Analytics'));
const Reports = React.lazy(() => import('./pages/Reports/Reports'));
const Settings = React.lazy(() => import('./pages/Settings/Settings'));
const Profile = React.lazy(() => import('./pages/Profile/Profile'));
const Login = React.lazy(() => import('./pages/Auth/Login'));
const Register = React.lazy(() => import('./pages/Auth/Register'));
const NotFound = React.lazy(() => import('./pages/NotFound/NotFound'));

// Services
import { initializeAnalytics } from './services/analytics';

// Styles
import './styles/globals.css';
import './styles/tailwind.css';

// Create QueryClient with optimized settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors
        if (error instanceof Error && error.message.includes('4')) {
          return false;
        }
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Initialize analytics
initializeAnalytics();

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <HelmetProvider>
        <Provider store={store}>
          <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <Router>
                <AuthProvider>
                  <WebSocketProvider>
                    <div className=\"App min-h-screen bg-gray-50\">
                      <Routes>
                        {/* Public routes */}
                        <Route
                          path=\"/login\"
                          element={
                            <Suspense fallback={<LoadingSpinner />}>
                              <Login />
                            </Suspense>
                          }
                        />
                        <Route
                          path=\"/register\"
                          element={
                            <Suspense fallback={<LoadingSpinner />}>
                              <Register />
                            </Suspense>
                          }
                        />

                        {/* Protected routes */}
                        <Route
                          path=\"/\"
                          element={
                            <ProtectedRoute>
                              <Layout />
                            </ProtectedRoute>
                          }
                        >
                          {/* Dashboard is the default route */}
                          <Route
                            index
                            element={
                              <Suspense fallback={<LoadingSpinner />}>
                                <Dashboard />
                              </Suspense>
                            }
                          />
                          <Route
                            path=\"dashboard\"
                            element={
                              <Suspense fallback={<LoadingSpinner />}>
                                <Dashboard />
                              </Suspense>
                            }
                          />
                          <Route
                            path=\"analytics\"
                            element={
                              <Suspense fallback={<LoadingSpinner />}>
                                <Analytics />
                              </Suspense>
                            }
                          />
                          <Route
                            path=\"reports\"
                            element={
                              <Suspense fallback={<LoadingSpinner />}>
                                <Reports />
                              </Suspense>
                            }
                          />
                          <Route
                            path=\"settings\"
                            element={
                              <Suspense fallback={<LoadingSpinner />}>
                                <Settings />
                              </Suspense>
                            }
                          />
                          <Route
                            path=\"profile\"
                            element={
                              <Suspense fallback={<LoadingSpinner />}>
                                <Profile />
                              </Suspense>
                            }
                          />
                        </Route>

                        {/* 404 route */}
                        <Route
                          path=\"/404\"
                          element={
                            <Suspense fallback={<LoadingSpinner />}>
                              <NotFound />
                            </Suspense>
                          }
                        />

                        {/* Redirect to 404 for unmatched routes */}
                        <Route path=\"*\" element={<Navigate to=\"/404\" replace />} />
                      </Routes>
                    </div>

                    {/* Global toast notifications */}
                    <Toaster
                      position=\"top-right\"
                      toastOptions={{
                        duration: 4000,
                        style: {
                          background: '#363636',
                          color: '#fff',
                        },
                        success: {
                          style: {
                            background: '#22c55e',
                          },
                        },
                        error: {
                          style: {
                            background: '#ef4444',
                          },
                        },
                      }}
                    />
                  </WebSocketProvider>
                </AuthProvider>
              </Router>
            </ThemeProvider>
            
            {/* React Query Devtools (development only) */}
            {process.env.NODE_ENV === 'development' && (
              <ReactQueryDevtools initialIsOpen={false} />
            )}
          </QueryClientProvider>
        </Provider>
      </HelmetProvider>
    </ErrorBoundary>
  );
};

export default App;