// API Service for DROPUX Sales System
import { API_BASE } from '../config/api.config';

class ApiService {
  constructor() {
    this.initializeAuth();
  }

  initializeAuth() {
    // Check if token exists and is valid
    const storedToken = localStorage.getItem('token');
    const storedExpiry = localStorage.getItem('token_expiry');
    
    if (storedToken && storedExpiry) {
      const now = new Date();
      const expiry = new Date(storedExpiry);
      
      // Check if token is expired
      if (now >= expiry) {
        console.log('🔒 Token expired, clearing auth');
        this.logout();
        return;
      }
      
      // Token is valid, set it
      this.token = storedToken;
      console.log('✅ Auth restored from localStorage');
    } else {
      this.token = null;
    }
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
      
      // Set expiration to 23:59 of current day in user's timezone
      const expiry = new Date();
      expiry.setHours(23, 59, 59, 999); // Set to 23:59:59.999 today
      
      // Store token and expiry
      localStorage.setItem('token', this.token);
      localStorage.setItem('token_expiry', expiry.toISOString());
      localStorage.setItem('user', JSON.stringify(response.user));
      
      console.log(`🔑 Token stored, expires at: ${expiry.toLocaleString()}`);
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
    localStorage.removeItem('token_expiry');
    localStorage.removeItem('user');
    console.log('🚪 Logged out, auth cleared');
  }

  // ML Stores
  async getMLStores() {
    return await this.request('/api/ml/my-stores');
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
    // Always check if token is expired before returning true
    if (!this.token) return false;
    
    const storedExpiry = localStorage.getItem('token_expiry');
    if (!storedExpiry) return false;
    
    const now = new Date();
    const expiry = new Date(storedExpiry);
    
    if (now >= expiry) {
      console.log('🔒 Token expired during check');
      this.logout();
      return false;
    }
    
    return true;
  }

  // Check token expiration and auto-logout if needed
  checkTokenExpiration() {
    const storedExpiry = localStorage.getItem('token_expiry');
    if (!storedExpiry || !this.token) return false;
    
    const now = new Date();
    const expiry = new Date(storedExpiry);
    
    if (now >= expiry) {
      console.log('🔒 Auto-logout: Token expired');
      this.logout();
      return false;
    }
    
    return true;
  }

  // Start periodic token validation
  startTokenValidation() {
    // Check every 30 seconds
    setInterval(() => {
      if (this.token) {
        this.checkTokenExpiration();
      }
    }, 30000);
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

// Start token validation when service is initialized
apiServiceInstance.startTokenValidation();

export default apiServiceInstance;