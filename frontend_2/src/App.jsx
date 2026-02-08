import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import SidebarLayout from './layouts/SidebarLayout';
import Dashboard from './pages/Dashboard';
import FullMap from './pages/FullMap';
import Alerts from './pages/Alerts';
import Reports from './pages/Reports';
import Landing from './pages/Landing';

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/landing" replace />;
};

// Public Route wrapper (redirect to dashboard if already authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return isAuthenticated ? <Navigate to="/" replace /> : children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Landing Page */}
      <Route path="/landing" element={
        <PublicRoute>
          <Landing />
        </PublicRoute>
      } />

      {/* Protected Routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <SidebarLayout>
            <Dashboard />
          </SidebarLayout>
        </ProtectedRoute>
      } />
      <Route path="/map" element={
        <ProtectedRoute>
          <SidebarLayout>
            <FullMap />
          </SidebarLayout>
        </ProtectedRoute>
      } />
      <Route path="/alerts" element={
        <ProtectedRoute>
          <SidebarLayout>
            <Alerts />
          </SidebarLayout>
        </ProtectedRoute>
      } />
      <Route path="/reports" element={
        <ProtectedRoute>
          <SidebarLayout>
            <Reports />
          </SidebarLayout>
        </ProtectedRoute>
      } />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/landing" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
