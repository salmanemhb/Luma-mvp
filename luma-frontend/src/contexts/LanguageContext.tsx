import React, { createContext, useContext, useState } from 'react';

type Language = 'en' | 'es';

interface Translations {
  [key: string]: string;
}

const translations: Record<Language, Translations> = {
  en: {
    'app.title': 'Luma',
    'nav.dashboard': 'Dashboard',
    'nav.upload': 'Upload',
    'nav.report': 'Report',
    'nav.admin': 'Admin',
    'nav.logout': 'Logout',
    'dashboard.title': 'Dashboard',
    'dashboard.totalEmissions': 'Total Emissions',
    'dashboard.scope1': 'Scope 1',
    'dashboard.scope2': 'Scope 2',
    'dashboard.scope3': 'Scope 3',
    'upload.title': 'Upload Documents',
    'upload.dropzone': 'Drop files here or click to browse',
    'upload.analyzing': 'Analyzing...',
    'report.title': 'CSRD Reports',
    'report.generate': 'Generate Report',
    'report.download': 'Download',
    'admin.activeCompanies': 'Active Companies',
    'admin.totalEmissions': 'Total Emissions (tCO₂e)',
    'admin.reportsGenerated': 'Reports Generated',
    'admin.uploadSuccess': 'Upload Success Rate',
  },
  es: {
    'app.title': 'Luma',
    'nav.dashboard': 'Panel',
    'nav.upload': 'Subir',
    'nav.report': 'Informes',
    'nav.admin': 'Admin',
    'nav.logout': 'Salir',
    'dashboard.title': 'Panel de Control',
    'dashboard.totalEmissions': 'Emisiones Totales',
    'dashboard.scope1': 'Alcance 1',
    'dashboard.scope2': 'Alcance 2',
    'dashboard.scope3': 'Alcance 3',
    'upload.title': 'Subir Documentos',
    'upload.dropzone': 'Arrastra archivos aquí o haz clic para buscar',
    'upload.analyzing': 'Analizando...',
    'report.title': 'Informes CSRD',
    'report.generate': 'Generar Informe',
    'report.download': 'Descargar',
    'admin.activeCompanies': 'Empresas Activas',
    'admin.totalEmissions': 'Emisiones Totales (tCO₂e)',
    'admin.reportsGenerated': 'Informes Generados',
    'admin.uploadSuccess': 'Tasa de Éxito de Subida',
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('es'); // Default to Spanish

  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
