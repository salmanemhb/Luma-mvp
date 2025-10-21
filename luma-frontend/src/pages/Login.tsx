import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Navbar } from '@/components/Navbar';
import { toast } from 'sonner';
import { Leaf } from 'lucide-react';

export const Auth = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Mock authentication for frontend-only mode
      await new Promise(resolve => setTimeout(resolve, 500));

      if (isLogin) {
        // Store user in localStorage
        localStorage.setItem('user', JSON.stringify({ email }));
        
        // Check if user is admin
        const adminEmails = ['admin@luma.eco'];
        if (adminEmails.includes(email)) {
          navigate('/admin');
        } else {
          navigate('/dashboard');
        }
        
        toast.success(t('auth.login') + ' successful!');
      } else {
        toast.success('Account created! You can now log in.');
        setIsLogin(true);
      }
    } catch (error: any) {
      toast.error('Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen gradient-hero">
      <Navbar />
      
      <div className="pt-32 pb-20 px-4 flex items-center justify-center">
        <Card className="card-elevated w-full max-w-md p-8 animate-fade-in">
          <div className="flex items-center justify-center mb-8">
            <div className="bg-primary p-3 rounded-lg">
              <Leaf className="h-8 w-8 text-primary-foreground" />
            </div>
          </div>
          
          <h2 className="text-3xl font-bold text-center mb-8">
            {isLogin ? t('auth.login') : t('auth.register')}
          </h2>

          <form onSubmit={handleAuth} className="space-y-6">
            <div>
              <label className="text-sm font-medium mb-2 block">
                {t('auth.email')}
              </label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">
                {t('auth.password')}
              </label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full"
              />
            </div>

            <Button
              type="submit"
              className="btn-hero w-full"
              disabled={loading}
            >
              {loading ? 'Loading...' : isLogin ? t('auth.signIn') : t('auth.signUp')}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-primary hover:underline"
            >
              {isLogin ? t('auth.noAccount') : t('auth.hasAccount')}
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
};
