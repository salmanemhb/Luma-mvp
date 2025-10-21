import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Navbar } from '@/components/Navbar';
import { KPICard } from '@/components/KPICard';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Title, Tooltip, ArcElement } from 'chart.js';
import { Line, Pie } from 'react-chartjs-2';
import { Activity, TrendingDown, TrendingUp, FileText } from 'lucide-react';
import { getDashboardData } from '@/lib/api';
import { uploadAPI } from '@/lib/api';
import { useNavigate } from 'react-router-dom';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement);

export const Dashboard = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [recentUploads, setRecentUploads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getDashboardData();
        const backendData = response.data;
        
        // Transform backend response to frontend format
        const transformedData = {
          total_emissions: backendData.summary?.total_co2e || 0,
          scope1: backendData.summary?.scope1_co2e || 0,
          scope2: backendData.summary?.scope2_co2e || 0,
          scope3: backendData.summary?.scope3_co2e || 0,
          data_coverage: backendData.summary?.data_coverage || 0,
          monthly_data: backendData.monthly_data?.map((item: any) => ({
            month: item.month ? new Date(item.month).toLocaleDateString('en', { month: 'short' }) : 'N/A',
            emissions: item.co2e || 0
          })) || [],
          category_breakdown: backendData.category_breakdown || [],
          top_suppliers: backendData.top_suppliers || [],
        };
        
        setData(transformedData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        // Use mock data for demo
        setData({
          total_emissions: 1234.5,
          scope1: 456.2,
          scope2: 389.1,
          scope3: 389.2,
          data_coverage: 87,
          monthly_data: [
            { month: 'Jan', emissions: 120 },
            { month: 'Feb', emissions: 110 },
            { month: 'Mar', emissions: 105 },
            { month: 'Apr', emissions: 98 },
            { month: 'May', emissions: 102 },
            { month: 'Jun', emissions: 95 }
          ],
          category_breakdown: [],
          top_suppliers: [],
        });
      } finally {
        setLoading(false);
      }
    };

    const fetchUploads = async () => {
      try {
        const response = await uploadAPI.listDocuments();
        setRecentUploads(response.data.documents?.slice(0, 5) || []);
      } catch (error) {
        console.error('Failed to fetch uploads:', error);
      }
    };

    fetchData();
    fetchUploads();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="pt-24 pb-12 px-4 max-w-7xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-muted rounded w-1/4"></div>
            <div className="grid md:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-32 bg-muted rounded-2xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const lineChartData = {
    labels: data?.monthly_data?.map((d: any) => d.month) || [],
    datasets: [
      {
        label: t('dashboard.monthlyEmissions'),
        data: data?.monthly_data?.map((d: any) => d.emissions) || [],
        borderColor: 'hsl(104, 15%, 68%)',
        backgroundColor: 'hsl(104, 15%, 68%, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const pieChartData = {
    labels: [t('dashboard.scope1'), t('dashboard.scope2'), t('dashboard.scope3')],
    datasets: [
      {
        data: [data?.scope1 || 0, data?.scope2 || 0, data?.scope3 || 0],
        backgroundColor: [
          'hsl(104, 15%, 68%)',
          'hsl(42, 34%, 63%)',
          'hsl(104, 20%, 80%)',
        ],
      },
    ],
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="pt-24 pb-12 px-4 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold">{t('dashboard.title')}</h1>
          <Button onClick={() => navigate('/report')} className="btn-hero">
            <FileText className="mr-2 h-5 w-5" />
            {t('dashboard.generateReport')}
          </Button>
        </div>

        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <KPICard
            title={t('dashboard.totalEmissions')}
            value={`${data?.total_emissions || 0} tCO₂e`}
            icon={Activity}
            trend="-5.2% from last month"
          />
          <KPICard
            title={t('dashboard.scope1')}
            value={`${data?.scope1 || 0} tCO₂e`}
            icon={TrendingUp}
          />
          <KPICard
            title={t('dashboard.scope2')}
            value={`${data?.scope2 || 0} tCO₂e`}
            icon={TrendingDown}
          />
          <KPICard
            title={t('dashboard.dataCoverage')}
            value={`${data?.data_coverage || 0}%`}
            icon={Activity}
          />
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="card-elevated p-6 animate-slide-up">
            <h3 className="text-xl font-semibold mb-4">{t('dashboard.monthlyEmissions')}</h3>
            <Line data={lineChartData} options={{ responsive: true, maintainAspectRatio: true }} />
          </Card>

          <Card className="card-elevated p-6 animate-slide-up">
            <h3 className="text-xl font-semibold mb-4">{t('dashboard.scopeBreakdown')}</h3>
            <Pie data={pieChartData} options={{ responsive: true, maintainAspectRatio: true }} />
          </Card>
        </div>

        <Card className="card-elevated p-6 animate-slide-up">
          <h3 className="text-xl font-semibold mb-4">{t('dashboard.recentUploads')}</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4">File</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {recentUploads.length > 0 ? (
                  recentUploads.map((upload: any) => (
                    <tr key={upload.id} className="border-b border-border/50">
                      <td className="py-3 px-4">{upload.filename}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          upload.status === 'processed' 
                            ? 'bg-primary/10 text-primary' 
                            : upload.status === 'processing'
                            ? 'bg-secondary/10 text-secondary'
                            : 'bg-muted text-muted-foreground'
                        }`}>
                          {upload.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {upload.uploaded_at ? new Date(upload.uploaded_at).toLocaleDateString() : '-'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} className="py-8 text-center text-muted-foreground">
                      No documents uploaded yet. <a href="/upload" className="text-primary hover:underline">Upload your first document</a>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
};
