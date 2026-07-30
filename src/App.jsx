import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './components/Toast';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import SalesPage from './pages/SalesPage';
import PredictionPage from './pages/PredictionPage';
import AnalyticsPage from './pages/AnalyticsPage';

// ----------------------------------------
// Page metadata for TopNav
// ----------------------------------------
const PAGE_META = {
  '/': {
    title: 'Dashboard Summary',
    description: 'Real-time statistics & visual forecasts',
  },
  '/sales': {
    title: 'Sales Management',
    description: 'Add, modify, and delete transactions in database',
  },
  '/prediction': {
    title: 'AI Forecasting',
    description: 'Predict future monthly sales based on Machine Learning',
  },
  '/analytics': {
    title: 'Sales Graph Analysis',
    description: 'Historical data and actual vs prediction models',
  },
};

// ----------------------------------------
// Protected Layout (sidebar + content)
// ----------------------------------------
function AppLayout() {
  const location = useLocation();
  const meta = PAGE_META[location.pathname] || PAGE_META['/'];

  return (
    <div className="app-container">
      <Sidebar />
      <main className="content-area">
        <TopNav title={meta.title} description={meta.description} />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/sales" element={<SalesPage />} />
          <Route path="/prediction" element={<PredictionPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

// ----------------------------------------
// Auth Gate
// ----------------------------------------
function AuthGate() {
  const { isLoggedIn, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#0B0F19',
        color: '#94A3B8',
        fontFamily: 'Outfit, sans-serif',
        fontSize: '16px',
      }}>
        <i className="fa-solid fa-spinner fa-spin" style={{ marginRight: '10px' }} />
        Loading...
      </div>
    );
  }

  if (!isLoggedIn) {
    return <LoginPage />;
  }

  return <AppLayout />;
}

// ----------------------------------------
// Root App
// ----------------------------------------
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <AuthGate />
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
