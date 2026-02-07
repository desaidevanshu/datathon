import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SidebarLayout from './layouts/SidebarLayout';
import Dashboard from './pages/Dashboard';
import FullMap from './pages/FullMap';

function App() {
  return (
    <Router>
      <SidebarLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/map" element={<FullMap />} />
          {/* Add other placeholders if needed */}
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </SidebarLayout>
    </Router>
  );
}

export default App;
