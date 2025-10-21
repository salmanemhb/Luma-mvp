import { useTranslation } from 'react-i18next';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Download, FileSpreadsheet } from 'lucide-react';
import { toast } from 'sonner';

export const Report = () => {
  const { t } = useTranslation();

  const handleDownload = (type: 'pdf' | 'excel') => {
    toast.success(`Downloading ${type.toUpperCase()} report...`);
    // In production, this would trigger actual file download from API
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="pt-24 pb-12 px-4 max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 animate-fade-in">{t('report.title')}</h1>

        <Card className="card-elevated p-8 animate-slide-up mb-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-semibold mb-2">Q2 2024 Sustainability Report</h2>
              <p className="text-muted-foreground">{t('report.period')}: April - June 2024</p>
            </div>
            <div className="flex gap-3">
              <Button onClick={() => handleDownload('pdf')} className="btn-hero">
                <Download className="mr-2 h-4 w-4" />
                {t('report.download')}
              </Button>
              <Button onClick={() => handleDownload('excel')} className="btn-secondary">
                <FileSpreadsheet className="mr-2 h-4 w-4" />
                {t('report.downloadExcel')}
              </Button>
            </div>
          </div>

          <div className="border-2 border-border rounded-xl p-8 bg-muted/10">
            <div className="aspect-[8.5/11] bg-card rounded-lg shadow-lg flex items-center justify-center">
              <p className="text-muted-foreground">Report Preview</p>
            </div>
          </div>
        </Card>

        <Card className="card-elevated p-6 animate-slide-up">
          <h3 className="text-xl font-semibold mb-4">Report Metadata</h3>
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b border-border/50">
              <span className="text-muted-foreground">{t('report.period')}</span>
              <span className="font-medium">Q2 2024</span>
            </div>
            <div className="flex justify-between py-2 border-b border-border/50">
              <span className="text-muted-foreground">{t('report.methodology')}</span>
              <span className="font-medium">GHG Protocol</span>
            </div>
            <div className="flex justify-between py-2 border-b border-border/50">
              <span className="text-muted-foreground">{t('report.emissionFactors')}</span>
              <span className="font-medium">DEFRA 2024</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-muted-foreground">Generated</span>
              <span className="font-medium">{new Date().toLocaleDateString()}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
