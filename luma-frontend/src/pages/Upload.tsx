import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Upload as UploadIcon, FileText, CheckCircle } from 'lucide-react';
import { uploadFile, analyzeData } from '@/lib/api';
import { toast } from 'sonner';

export const Upload = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [files, setFiles] = useState<File[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg']
    },
    multiple: true
  });

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setProgress(0);

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setProgress(((i + 1) / files.length) * 50);
        
        const uploadResponse = await uploadFile(file);
        const uploadId = uploadResponse.data.upload_id;
        
        setProgress(50 + ((i + 1) / files.length) * 50);
        await analyzeData(uploadId);
      }

      toast.success(t('upload.success'));
      setTimeout(() => navigate('/dashboard'), 1000);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || t('upload.error'));
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="pt-24 pb-12 px-4 max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 animate-fade-in">{t('upload.title')}</h1>

        <Card className="card-elevated p-8 animate-slide-up">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
              isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
            }`}
          >
            <input {...getInputProps()} />
            <UploadIcon className="h-16 w-16 mx-auto mb-4 text-primary" />
            <p className="text-lg mb-2">{t('upload.dropzone')}</p>
            <p className="text-sm text-muted-foreground">{t('upload.acceptedFormats')}</p>
          </div>

          {files.length > 0 && (
            <div className="mt-6 space-y-3">
              {files.map((file, idx) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
                  <FileText className="h-5 w-5 text-primary" />
                  <span className="flex-1 text-sm">{file.name}</span>
                  <CheckCircle className="h-5 w-5 text-primary" />
                </div>
              ))}
            </div>
          )}

          {uploading && (
            <div className="mt-6">
              <Progress value={progress} className="h-2" />
              <p className="text-sm text-muted-foreground mt-2 text-center">
                {t('upload.uploading')} {Math.round(progress)}%
              </p>
            </div>
          )}

          <Button
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            className="btn-hero w-full mt-6"
          >
            {uploading ? t('upload.uploading') : 'Upload Files'}
          </Button>
        </Card>
      </div>
    </div>
  );
};
