import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { LayoutDashboard, Upload, FileText, Settings, LogOut, Globe } from 'lucide-react';
import { Button } from './ui/button';

const Layout = () => {
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const location = useLocation();

  const navigation = [
    { name: t('nav.dashboard'), href: '/dashboard', icon: LayoutDashboard },
    { name: t('nav.upload'), href: '/upload', icon: Upload },
    { name: t('nav.report'), href: '/report', icon: FileText },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gradient-to-br from-sage-50 via-white to-gold-50">
      {/* Top Navigation */}
      <nav className="bg-white shadow-sm border-b border-sage-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-sage-600 to-gold-500 bg-clip-text text-transparent">
                  {t('app.title')}
                </h1>
              </div>
              <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                        isActive(item.href)
                          ? 'bg-sage-100 text-sage-900'
                          : 'text-gray-700 hover:bg-sage-50 hover:text-sage-900'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.name}
                    </Link>
                  );
                })}
                
                {/* Admin link if admin */}
                {user && (
                  <Link
                    to="/admin"
                    className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      location.pathname.startsWith('/admin')
                        ? 'bg-sage-100 text-sage-900'
                        : 'text-gray-700 hover:bg-sage-50 hover:text-sage-900'
                    }`}
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    {t('nav.admin')}
                  </Link>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Language Switcher */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setLanguage(language === 'en' ? 'es' : 'en')}
              >
                <Globe className="w-4 h-4 mr-2" />
                {language.toUpperCase()}
              </Button>
              
              {/* User info */}
              <div className="text-sm text-gray-700">
                {user?.email}
              </div>
              
              {/* Logout */}
              <Button variant="outline" size="sm" onClick={logout}>
                <LogOut className="w-4 h-4 mr-2" />
                {t('nav.logout')}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
