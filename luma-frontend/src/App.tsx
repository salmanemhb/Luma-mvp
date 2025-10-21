import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { Toaster } from './components/ui/toaster';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Report from './pages/Report';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminCompanies from './pages/admin/AdminCompanies';
import AdminCompanyDetail from './pages/admin/AdminCompanyDetail';
import AdminActivity from './pages/admin/AdminActivity';
import AdminInsights from './pages/admin/AdminInsights';
import AdminWaitlist from './pages/admin/AdminWaitlist';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <Router>
          <Toaster />
          <Routes>
            <Route path="/login" element={<Login />} />
            
            {/* Protected routes */}
            <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/report" element={<Report />} />
              
              {/* Admin routes */}
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin/companies" element={<AdminCompanies />} />
              <Route path="/admin/company/:id" element={<AdminCompanyDetail />} />
              <Route path="/admin/activity" element={<AdminActivity />} />
              <Route path="/admin/insights" element={<AdminInsights />} />
              <Route path="/admin/waitlist" element={<AdminWaitlist />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
