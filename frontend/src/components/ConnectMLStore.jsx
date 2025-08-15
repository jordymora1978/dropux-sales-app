import React, { useState, useEffect } from 'react';
import { 
  Store, 
  ExternalLink, 
  Copy, 
  CheckCircle, 
  AlertCircle, 
  Loader, 
  Settings,
  Globe,
  Key,
  Shield,
  RefreshCw
} from 'lucide-react';
import apiService from '../services/api';
import './ConnectMLStore.css';

const ConnectMLStore = ({ onClose, onSuccess }) => {
  // Form states
  const [formData, setFormData] = useState({
    site_id: '',
    app_id: '',
    app_secret: '',
    store_name: ''
  });
  
  // UI states
  const [step, setStep] = useState(1); // 1: Form, 2: Instructions, 3: Connecting
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [authUrl, setAuthUrl] = useState('');
  const [redirectUri, setRedirectUri] = useState('');
  const [copied, setCopied] = useState(false);
  const [instructions, setInstructions] = useState([]);
  
  // Popup cleanup on component unmount
  useEffect(() => {
    return () => {
      // Clean up popup if component unmounts
      if (window.mlAuthPopup && !window.mlAuthPopup.closed) {
        window.mlAuthPopup.close();
      }
    };
  }, []);

  // Load available ML sites
  useEffect(() => {
    loadSites();
  }, []);

  const loadSites = async () => {
    try {
      const response = await apiService.request('/api/ml/sites');
      setSites(response.sites || []);
    } catch (error) {
      console.error('Error loading sites:', error);
      setError('Error cargando países disponibles');
    }
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Validate form
  const validateForm = () => {
    if (!formData.site_id) {
      setError('Selecciona un país');
      return false;
    }
    if (!formData.app_id || formData.app_id.length < 10) {
      setError('App ID debe tener al menos 10 dígitos');
      return false;
    }
    if (!formData.app_secret || formData.app_secret.length < 20) {
      setError('App Secret debe tener al menos 20 caracteres');
      return false;
    }
    if (!formData.store_name.trim()) {
      setError('Nombre de tienda es requerido');
      return false;
    }
    return true;
  };

  // Submit form and get OAuth URL
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await apiService.request('/api/ml/connect-store', {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      
      setAuthUrl(response.auth_url);
      setRedirectUri(response.redirect_uri);
      setInstructions(response.instructions || []);
      setStep(2);
      
    } catch (error) {
      setError(error.message || 'Error configurando la conexión');
    } finally {
      setLoading(false);
    }
  };

  // Copy redirect URI to clipboard
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(redirectUri);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = redirectUri;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Open ML authorization in new window
  const openMLAuth = () => {
    setStep(3);
    setError('');
    
    // Close any existing popup
    if (window.mlAuthPopup && !window.mlAuthPopup.closed) {
      window.mlAuthPopup.close();
    }
    
    // Open popup with specific features
    const authWindow = window.open(
      authUrl,
      'ml_auth',
      'width=600,height=700,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no'
    );
    
    // Store reference globally
    window.mlAuthPopup = authWindow;
    
    // Listen for messages from popup
    const handleMessage = (event) => {
      // Verify origin for security
      const allowedOrigins = [
        'https://api.dropux.co',
        'http://localhost:8000',
        'http://127.0.0.1:8000'
      ];
      
      if (!allowedOrigins.includes(event.origin)) {
        console.log('❌ Message from unauthorized origin:', event.origin);
        return;
      }
      
      if (event.data.type === 'ML_CONNECTION_SUCCESS') {
        console.log('✅ ML Connection successful:', event.data);
        
        // Close popup
        if (authWindow && !authWindow.closed) {
          authWindow.close();
        }
        
        // Clean up
        window.removeEventListener('message', handleMessage);
        
        // Notify parent component
        if (onSuccess) {
          onSuccess();
        }
        
        // Close modal
        onClose();
      } else if (event.data.type === 'ML_CONNECTION_ERROR') {
        console.log('❌ ML Connection error:', event.data);
        setError(event.data.message || 'Error en la conexión con MercadoLibre');
        setStep(2); // Go back to instructions
        
        // Close popup
        if (authWindow && !authWindow.closed) {
          authWindow.close();
        }
        
        // Clean up
        window.removeEventListener('message', handleMessage);
      }
    };
    
    // Add message listener
    window.addEventListener('message', handleMessage);
    
    // Fallback: Check if popup was closed manually
    const checkClosed = setInterval(() => {
      if (authWindow.closed) {
        clearInterval(checkClosed);
        window.removeEventListener('message', handleMessage);
        
        // If closed manually without success message, go back to instructions
        setTimeout(() => {
          setStep(2);
          setError('Conexión cancelada. Intenta de nuevo si no completaste la autorización.');
        }, 500);
      }
    }, 1000);
    
    // Focus on popup
    authWindow.focus();
  };

  // Get site info by ID
  const getSiteInfo = (siteId) => {
    return sites.find(site => site.site_id === siteId) || {};
  };

  return (
    <div className="ml-connect-overlay">
      <div className="ml-connect-modal">
        {/* Header */}
        <div className="ml-connect-header">
          <div className="header-icon">
            <Store size={24} />
          </div>
          <div className="header-content">
            <h2>Conectar Tienda MercadoLibre</h2>
            <p>Conecta tu tienda de MercadoLibre para gestionar órdenes y productos</p>
          </div>
          <button className="close-btn" onClick={() => {
            // Clean up popup before closing
            if (window.mlAuthPopup && !window.mlAuthPopup.closed) {
              window.mlAuthPopup.close();
            }
            onClose();
          }}>×</button>
        </div>

        {/* Content based on step */}
        <div className="ml-connect-content">
          
          {/* Step 1: Configuration Form */}
          {step === 1 && (
            <>
              <div className="step-indicator">
                <span className="step active">1</span>
                <span className="step-line"></span>
                <span className="step">2</span>
                <span className="step-line"></span>
                <span className="step">3</span>
              </div>

              <form onSubmit={handleSubmit} className="ml-connect-form">
                
                {/* Country Selection */}
                <div className="form-group">
                  <label className="form-label">
                    <Globe size={16} />
                    País de MercadoLibre
                  </label>
                  <select 
                    name="site_id"
                    value={formData.site_id}
                    onChange={handleInputChange}
                    className="form-select"
                    required
                  >
                    <option value="">Selecciona un país</option>
                    {sites.map(site => (
                      <option key={site.site_id} value={site.site_id}>
                        {site.flag} {site.country} ({site.site_id})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Store Name */}
                <div className="form-group">
                  <label className="form-label">
                    <Store size={16} />
                    Nombre de la Tienda
                  </label>
                  <input
                    type="text"
                    name="store_name"
                    value={formData.store_name}
                    onChange={handleInputChange}
                    placeholder="Ej: Mi Tienda Principal"
                    className="form-input"
                    required
                  />
                  <span className="form-hint">Nombre para identificar esta tienda en Dropux</span>
                </div>

                {/* App ID */}
                <div className="form-group">
                  <label className="form-label">
                    <Key size={16} />
                    App ID
                  </label>
                  <input
                    type="text"
                    name="app_id"
                    value={formData.app_id}
                    onChange={handleInputChange}
                    placeholder="Ej: 1234567890123456"
                    className="form-input"
                    required
                  />
                  <span className="form-hint">ID de tu aplicación en ML Developers</span>
                </div>

                {/* App Secret */}
                <div className="form-group">
                  <label className="form-label">
                    <Shield size={16} />
                    App Secret
                  </label>
                  <input
                    type="password"
                    name="app_secret"
                    value={formData.app_secret}
                    onChange={handleInputChange}
                    placeholder="Tu App Secret de ML Developers"
                    className="form-input"
                    required
                  />
                  <span className="form-hint">Clave secreta de tu aplicación (se encripta automáticamente)</span>
                </div>

                {/* Error Display */}
                {error && (
                  <div className="error-message">
                    <AlertCircle size={16} />
                    {error}
                  </div>
                )}

                {/* Submit Button */}
                <button 
                  type="submit" 
                  className="submit-btn"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader size={16} className="spinner" />
                      Configurando...
                    </>
                  ) : (
                    <>
                      <Settings size={16} />
                      Configurar Conexión
                    </>
                  )}
                </button>
              </form>

              {/* Help Section */}
              <div className="help-section">
                <h4>¿Necesitas ayuda para obtener tu App ID y Secret?</h4>
                <p>
                  Visita <a href="https://developers.mercadolibre.com" target="_blank" rel="noopener noreferrer">
                    ML Developers <ExternalLink size={12} />
                  </a> y crea una nueva aplicación.
                </p>
              </div>
            </>
          )}

          {/* Step 2: Instructions */}
          {step === 2 && (
            <>
              <div className="step-indicator">
                <span className="step completed">✓</span>
                <span className="step-line"></span>
                <span className="step active">2</span>
                <span className="step-line"></span>
                <span className="step">3</span>
              </div>

              <div className="instructions-section">
                <h3>Configurar Redirect URI</h3>
                <p>Antes de autorizar, debes configurar la URI de redirección en tu aplicación ML:</p>

                {/* Copy Redirect URI */}
                <div className="redirect-uri-box">
                  <label>Redirect URI a configurar:</label>
                  <div className="copy-box">
                    <input 
                      type="text" 
                      value={redirectUri} 
                      readOnly 
                      className="redirect-input"
                    />
                    <button 
                      type="button" 
                      onClick={copyToClipboard}
                      className="copy-btn"
                    >
                      {copied ? <CheckCircle size={16} /> : <Copy size={16} />}
                      {copied ? 'Copiado' : 'Copiar'}
                    </button>
                  </div>
                </div>

                {/* Step by step instructions */}
                <div className="instructions-list">
                  {instructions.map((instruction, index) => (
                    <div key={index} className="instruction-item">
                      <span className="instruction-number">{index + 1}</span>
                      <span className="instruction-text">{instruction}</span>
                    </div>
                  ))}
                </div>

                {/* Action Buttons */}
                <div className="action-buttons">
                  <button 
                    type="button" 
                    onClick={() => setStep(1)}
                    className="back-btn"
                  >
                    Volver
                  </button>
                  <button 
                    type="button" 
                    onClick={openMLAuth}
                    className="connect-btn"
                  >
                    <ExternalLink size={16} />
                    Conectar Ahora
                  </button>
                </div>
              </div>
            </>
          )}

          {/* Step 3: Connecting */}
          {step === 3 && (
            <>
              <div className="step-indicator">
                <span className="step completed">✓</span>
                <span className="step-line"></span>
                <span className="step completed">✓</span>
                <span className="step-line"></span>
                <span className="step active">3</span>
              </div>

              <div className="connecting-section">
                <div className="connecting-animation">
                  <RefreshCw size={48} className="spinner large" />
                </div>
                <h3>Conectando con MercadoLibre</h3>
                <p>
                  Se abrió una ventana para autorizar la conexión. <br/>
                  <strong>Autoriza el acceso en la ventana emergente</strong> y esta ventana se cerrará automáticamente.
                </p>
                
                {/* Error Display */}
                {error && (
                  <div className="error-message">
                    <AlertCircle size={16} />
                    {error}
                  </div>
                )}
                
                <div className="connecting-info">
                  <div className="info-item">
                    <span className="info-label">País:</span>
                    <span className="info-value">
                      {getSiteInfo(formData.site_id).flag} {getSiteInfo(formData.site_id).country}
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Tienda:</span>
                    <span className="info-value">{formData.store_name}</span>
                  </div>
                </div>
                
                {/* Cancel Button */}
                <div className="action-buttons">
                  <button 
                    type="button" 
                    onClick={() => {
                      // Close popup and go back
                      if (window.mlAuthPopup && !window.mlAuthPopup.closed) {
                        window.mlAuthPopup.close();
                      }
                      setStep(2);
                      setError('');
                    }}
                    className="back-btn"
                  >
                    Cancelar
                  </button>
                  <button 
                    type="button" 
                    onClick={openMLAuth}
                    className="connect-btn secondary"
                  >
                    <ExternalLink size={16} />
                    Abrir Ventana de Nuevo
                  </button>
                </div>
              </div>
            </>
          )}

        </div>
      </div>
    </div>
  );
};

export default ConnectMLStore;