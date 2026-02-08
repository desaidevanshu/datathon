import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Overview from './pages/Overview';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import FullMap from './pages/FullMap';
import Analysis from './pages/Analysis';
import Alerts from './pages/Alerts';
import Reports from './pages/Reports';

import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Landing Page */}
          <Route path="/" element={<Overview />} />

          {/* Protected Dashboard Routes */}
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<Navigate to="monitoring" replace />} />
            <Route path="monitoring" element={<Dashboard />} />
            <Route path="map" element={<FullMap />} />
            <Route path="analysis" element={<Analysis />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="reports" element={<Reports />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
