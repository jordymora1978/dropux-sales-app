// API Configuration for DROPUX Sales System
// This file centralizes all API configuration

const API_URLS = {
  // Production backends (in order of preference)
  production: [
    'https://web-production-ae7da.up.railway.app',  // Railway actual domain
    'https://api.dropux.co',                        // Custom domain (when DNS is fixed)
  ],
  // Development backends
  development: [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
  ]
};

// Determine environment
const isProduction = process.env.NODE_ENV === 'production' || 
                    process.env.REACT_APP_ENV === 'production';

// Get API URL from environment or use defaults
const getApiUrl = () => {
  // First, check if there's an explicit env variable
  if (process.env.REACT_APP_API_URL) {
    console.log('Using API URL from env:', process.env.REACT_APP_API_URL);
    return process.env.REACT_APP_API_URL;
  }
  
  // Otherwise, use the first URL from the appropriate environment
  const urls = isProduction ? API_URLS.production : API_URLS.development;
  const selectedUrl = urls[0];
  
  console.log('Using default API URL:', selectedUrl);
  return selectedUrl;
};

export const API_BASE = getApiUrl();

// Export for debugging
export const API_CONFIG = {
  API_BASE,
  IS_PRODUCTION: isProduction,
  ENV: process.env.NODE_ENV,
  REACT_APP_ENV: process.env.REACT_APP_ENV,
  CONFIGURED_URL: process.env.REACT_APP_API_URL,
};

// Log configuration on app start
console.log('🚀 DROPUX API Configuration:', API_CONFIG);