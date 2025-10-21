import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      nav: {
        home: 'Home',
        upload: 'Upload',
        dashboard: 'Dashboard',
        report: 'Report',
        admin: 'Admin',
        login: 'Login',
        logout: 'Logout'
      },
      hero: {
        title: 'Automate Your Sustainability Reporting',
        subtitle: 'Simplify CSRD compliance for EU manufacturing SMEs with AI-powered ESG data automation',
        joinBeta: 'Join Beta',
        loginToDashboard: 'Login to Dashboard'
      },
      howItWorks: {
        title: 'How It Works',
        step1: 'Upload Your Data',
        step1desc: 'Drag and drop utility bills, invoices, and operational data',
        step2: 'AI Analysis',
        step2desc: 'Our AI extracts and categorizes emissions data automatically',
        step3: 'Generate Reports',
        step3desc: 'CSRD-compliant reports ready in minutes'
      },
      whyLuma: {
        title: 'Why Luma?',
        reason1: 'Save Time',
        reason1desc: 'Reduce reporting time by 80%',
        reason2: 'Stay Compliant',
        reason2desc: 'Always up-to-date with latest CSRD standards',
        reason3: 'Gain Insights',
        reason3desc: 'Visualize your sustainability journey'
      },
      auth: {
        login: 'Login',
        register: 'Create Account',
        email: 'Email',
        password: 'Password',
        forgotPassword: 'Forgot password?',
        noAccount: "Don't have an account?",
        hasAccount: 'Already have an account?',
        signUp: 'Sign up',
        signIn: 'Sign in'
      },
      upload: {
        title: 'Upload Data',
        dropzone: 'Drag and drop files here, or click to select',
        acceptedFormats: 'Accepted formats: PDF, CSV, XLSX, PNG, JPG',
        uploading: 'Uploading...',
        success: 'Upload successful!',
        error: 'Upload failed. Please try again.'
      },
      dashboard: {
        title: 'Dashboard',
        totalEmissions: 'Total Emissions',
        scope1: 'Scope 1',
        scope2: 'Scope 2',
        scope3: 'Scope 3',
        dataCoverage: 'Data Coverage',
        monthlyEmissions: 'Monthly Emissions Trend',
        scopeBreakdown: 'Scope Breakdown',
        recentUploads: 'Recent Uploads',
        generateReport: 'Generate Report'
      },
      report: {
        title: 'Sustainability Report',
        download: 'Download PDF',
        downloadExcel: 'Download Excel',
        period: 'Report Period',
        methodology: 'Methodology',
        emissionFactors: 'Emission Factors Used'
      },
      admin: {
        title: 'Admin Dashboard',
        companies: 'Companies',
        activity: 'Activity',
        insights: 'Insights',
        export: 'Export Data',
        activeCompanies: 'Active Companies',
        totalEmissions: 'Total Emissions (tCO₂e)',
        reportsGenerated: 'Reports Generated',
        topCompanies: 'Top Companies by Emissions',
        monthlyTotals: 'Monthly Totals'
      },
      footer: {
        about: 'About',
        contact: 'Contact',
        privacy: 'Privacy Policy',
        terms: 'Terms of Service'
      }
    }
  },
  es: {
    translation: {
      nav: {
        home: 'Inicio',
        upload: 'Subir',
        dashboard: 'Panel',
        report: 'Informe',
        admin: 'Admin',
        login: 'Iniciar Sesión',
        logout: 'Cerrar Sesión'
      },
      hero: {
        title: 'Automatiza tu Reporte de Sostenibilidad',
        subtitle: 'Simplifica el cumplimiento de CSRD para PYMEs manufactureras de la UE con automatización de datos ESG',
        joinBeta: 'Únete a Beta',
        loginToDashboard: 'Ir al Panel'
      },
      howItWorks: {
        title: 'Cómo Funciona',
        step1: 'Sube tus Datos',
        step1desc: 'Arrastra facturas de servicios y datos operacionales',
        step2: 'Análisis con IA',
        step2desc: 'Nuestra IA extrae y categoriza datos de emisiones automáticamente',
        step3: 'Genera Informes',
        step3desc: 'Informes conformes a CSRD listos en minutos'
      },
      whyLuma: {
        title: '¿Por Qué Luma?',
        reason1: 'Ahorra Tiempo',
        reason1desc: 'Reduce el tiempo de reporte en un 80%',
        reason2: 'Mantente Conforme',
        reason2desc: 'Siempre actualizado con los estándares CSRD',
        reason3: 'Obtén Insights',
        reason3desc: 'Visualiza tu viaje de sostenibilidad'
      },
      auth: {
        login: 'Iniciar Sesión',
        register: 'Crear Cuenta',
        email: 'Correo Electrónico',
        password: 'Contraseña',
        forgotPassword: '¿Olvidaste tu contraseña?',
        noAccount: '¿No tienes cuenta?',
        hasAccount: '¿Ya tienes cuenta?',
        signUp: 'Registrarse',
        signIn: 'Iniciar sesión'
      },
      upload: {
        title: 'Subir Datos',
        dropzone: 'Arrastra archivos aquí o haz clic para seleccionar',
        acceptedFormats: 'Formatos aceptados: PDF, CSV, XLSX, PNG, JPG',
        uploading: 'Subiendo...',
        success: '¡Subida exitosa!',
        error: 'Error al subir. Inténtalo de nuevo.'
      },
      dashboard: {
        title: 'Panel de Control',
        totalEmissions: 'Emisiones Totales',
        scope1: 'Alcance 1',
        scope2: 'Alcance 2',
        scope3: 'Alcance 3',
        dataCoverage: 'Cobertura de Datos',
        monthlyEmissions: 'Tendencia de Emisiones Mensuales',
        scopeBreakdown: 'Desglose por Alcance',
        recentUploads: 'Subidas Recientes',
        generateReport: 'Generar Informe'
      },
      report: {
        title: 'Informe de Sostenibilidad',
        download: 'Descargar PDF',
        downloadExcel: 'Descargar Excel',
        period: 'Período del Informe',
        methodology: 'Metodología',
        emissionFactors: 'Factores de Emisión Utilizados'
      },
      admin: {
        title: 'Panel de Administración',
        companies: 'Empresas',
        activity: 'Actividad',
        insights: 'Análisis',
        export: 'Exportar Datos',
        activeCompanies: 'Empresas Activas',
        totalEmissions: 'Emisiones Totales (tCO₂e)',
        reportsGenerated: 'Informes Generados',
        topCompanies: 'Empresas con Más Emisiones',
        monthlyTotals: 'Totales Mensuales'
      },
      footer: {
        about: 'Acerca de',
        contact: 'Contacto',
        privacy: 'Política de Privacidad',
        terms: 'Términos de Servicio'
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
