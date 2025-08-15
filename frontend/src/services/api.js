// API Service for DROPUX Sales System
// Temporalmente usando el dominio de Railway directamente hasta que se arregle el DNS
const API_BASE = process.env.REACT_APP_API_URL || 'https://web-production-ae7da.up.railway.app';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (this.token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    console.log('🚀 API Request:', {
      url,
      method: config.method || 'GET',
      headers: config.headers,
      body: config.body
    });

    try {
      const response = await fetch(url, config);
      
      console.log('📡 Response Status:', response.status);
      console.log('📡 Response Headers:', response.headers);
      
      const responseText = await response.text();
      console.log('📡 Response Body:', responseText);
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, clear it
          this.logout();
          throw new Error('Session expired');
        }
        
        // Try to parse error message
        try {
          const errorData = JSON.parse(responseText);
          throw new Error(errorData.detail || `API Error: ${response.status}`);
        } catch {
          throw new Error(`API Error: ${response.status} - ${responseText}`);
        }
      }

      // Parse JSON response
      try {
        return JSON.parse(responseText);
      } catch {
        console.error('Failed to parse JSON:', responseText);
        throw new Error('Invalid JSON response from server');
      }
    } catch (error) {
      console.error('❌ API Request failed:', error);
      throw error;
    }
  }

  // Authentication
  async login(email, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    if (response.access_token) {
      this.token = response.access_token;
      localStorage.setItem('token', this.token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }

    return response;
  }

  async verifyToken() {
    try {
      const response = await this.request('/auth/me');
      return response;
    } catch (error) {
      this.logout();
      throw error;
    }
  }

  logout() {
    this.token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  // ML Stores
  async getMLStores() {
    return await this.request('/api/ml/stores');
  }

  async setupMLStore(storeData) {
    return await this.request('/api/ml/stores/setup', {
      method: 'POST',
      body: JSON.stringify(storeData),
    });
  }

  // System
  async getSystemStatus() {
    return await this.request('/status');
  }

  async getHealthCheck() {
    return await this.request('/health');
  }

  // Utility
  isAuthenticated() {
    return !!this.token;
  }

  getUser() {
    try {
      return JSON.parse(localStorage.getItem('user') || '{}');
    } catch {
      return {};
    }
  }
}

const apiServiceInstance = new ApiService();
export default apiServiceInstance;