import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LandingPage } from './pages/LandingPage';
import { Login } from './pages/Auth/Login';
import { Signup } from './pages/Auth/Signup';
import { StoreList } from './pages/Stores/StoreList';
import { StoreDetail } from './pages/StoreDetail/StoreDetail';
import { WidgetSettings } from './pages/Settings/WidgetSettings';
import { Analytics } from './pages/Analytics/Analytics';
import { ApiKeys } from './pages/Settings/ApiKeys';

// Route guards to protect console panel URL scopes
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-10 h-10 border-4 border-brand border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Route guard to prevent authenticated users visiting auth screens
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (isAuthenticated) {
    return <Navigate to="/stores" replace />;
  }

  return <>{children}</>;
};

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Pages */}
      <Route path="/" element={<LandingPage />} />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/signup"
        element={
          <PublicRoute>
            <Signup />
          </PublicRoute>
        }
      />

      {/* Protected Console Dashboard Pages */}
      <Route
        path="/stores"
        element={
          <ProtectedRoute>
            <StoreList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/stores/:storeId"
        element={
          <ProtectedRoute>
            <StoreDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/stores/:storeId/settings"
        element={
          <ProtectedRoute>
            <WidgetSettings />
          </ProtectedRoute>
        }
      />
      <Route
        path="/stores/:storeId/analytics"
        element={
          <ProtectedRoute>
            <Analytics />
          </ProtectedRoute>
        }
      />
      <Route
        path="/stores/:storeId/keys"
        element={
          <ProtectedRoute>
            <ApiKeys />
          </ProtectedRoute>
        }
      />

      {/* Wildcard redirects */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
