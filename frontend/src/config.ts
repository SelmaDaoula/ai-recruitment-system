// Configuration de l'API
const config = {
  apiUrl: import.meta.env.VITE_API_URL || '/api',
  environment: import.meta.env.VITE_ENVIRONMENT || 'development',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
};

export default config;