import React, { useState } from 'react';

const ConnectStore = () => {
  const [formData, setFormData] = useState({
    site_id: 'MLC', // Chile por defecto
    app_number: '',
    app_id: '',
    app_secret: '',
    store_name: ''
  });
  
  const [redirectUri, setRedirectUri] = useState('');
  const [loading, setLoading] = useState(false);

  const sites = [
    { value: 'MLA', label: 'Argentina' },
    { value: 'MLB', label: 'Brasil' },
    { value: 'MLC', label: 'Chile' },
    { value: 'MCO', label: 'Colombia' },
    { value: 'MCR', label: 'Costa Rica' },
    { value: 'MEC', label: 'Ecuador' },
    { value: 'MLM', label: 'México' },
    { value: 'MPA', label: 'Panamá' },
    { value: 'MPE', label: 'Perú' },
    { value: 'MPY', label: 'Paraguay' },
    { value: 'MLU', label: 'Uruguay' },
    { value: 'MLV', label: 'Venezuela' },
    { value: 'MBO', label: 'Bolivia' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('https://sales.dropux.co/api/ml/stores/setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      
      if (response.ok) {
        // Guardar redirect_uri para que el usuario la copie
        setRedirectUri(data.redirect_uri);
        
        // Abrir ventana de OAuth de MercadoLibre
        setTimeout(() => {
          window.open(data.auth_url, '_blank', 'width=600,height=700');
        }, 2000);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error al configurar la tienda');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="connect-store-container">
      <div className="card">
        <h2>Conectar a la Tienda</h2>
        <p className="subtitle">Seleccione el sitio con el que desea conectarse.</p>
        
        <form onSubmit={handleSubmit}>
          {/* País/Sitio */}
          <div className="form-group">
            <label>País</label>
            <select 
              value={formData.site_id}
              onChange={(e) => setFormData({...formData, site_id: e.target.value})}
              required
            >
              {sites.map(site => (
                <option key={site.value} value={site.value}>
                  {site.label}
                </option>
              ))}
            </select>
          </div>

          {/* App Number */}
          <div className="form-group">
            <label>App Number</label>
            <input
              type="text"
              value={formData.app_number}
              onChange={(e) => setFormData({...formData, app_number: e.target.value})}
              placeholder="Ej: 1234567890"
              required
            />
          </div>

          {/* App ID (Client ID) */}
          <div className="form-group">
            <label>App ID</label>
            <input
              type="text"
              value={formData.app_id}
              onChange={(e) => setFormData({...formData, app_id: e.target.value})}
              placeholder="Ej: 6996757760934434"
              required
            />
          </div>

          {/* App Secret */}
          <div className="form-group">
            <label>App Secret</label>
            <input
              type="password"
              value={formData.app_secret}
              onChange={(e) => setFormData({...formData, app_secret: e.target.value})}
              placeholder="Tu App Secret de MercadoLibre"
              required
            />
          </div>

          {/* Store Name (opcional) */}
          <div className="form-group">
            <label>Nombre de la Tienda (opcional)</label>
            <input
              type="text"
              value={formData.store_name}
              onChange={(e) => setFormData({...formData, store_name: e.target.value})}
              placeholder="Ej: Mi Tienda Principal"
            />
          </div>

          {/* Redirect URI generada */}
          {redirectUri && (
            <div className="redirect-uri-container">
              <label>Redirect URI</label>
              <div className="input-with-copy">
                <input 
                  type="text" 
                  value={redirectUri} 
                  readOnly 
                  className="redirect-uri-input"
                />
                <button 
                  type="button"
                  onClick={() => navigator.clipboard.writeText(redirectUri)}
                  className="copy-button"
                >
                  📋 Copiar
                </button>
              </div>
              <p className="help-text">
                ⚠️ Por favor, configure esta URI de redirección en su campo 
                "URI de redirección de MercadoLibre" en developers.mercadolibre.com
              </p>
            </div>
          )}

          {/* Botón Connect */}
          <button 
            type="submit" 
            className="connect-button"
            disabled={loading}
          >
            {loading ? 'CONECTANDO...' : 'CONNECT'}
          </button>
        </form>

        {/* Instrucciones */}
        <div className="instructions">
          <h3>📋 Instrucciones:</h3>
          <ol>
            <li>Vaya a <a href="https://developers.mercadolibre.com" target="_blank">developers.mercadolibre.com</a></li>
            <li>Cree una nueva aplicación</li>
            <li>Copie el App ID y App Secret</li>
            <li>Pegue la Redirect URI generada en su aplicación de ML</li>
            <li>Haga clic en CONNECT</li>
          </ol>
        </div>
      </div>

      <style jsx>{`
        .connect-store-container {
          max-width: 600px;
          margin: 50px auto;
          padding: 20px;
        }

        .card {
          background: white;
          border-radius: 10px;
          padding: 30px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h2 {
          color: #333;
          margin-bottom: 10px;
        }

        .subtitle {
          color: #666;
          margin-bottom: 30px;
        }

        .form-group {
          margin-bottom: 20px;
        }

        label {
          display: block;
          margin-bottom: 5px;
          font-weight: 600;
          color: #555;
        }

        input, select {
          width: 100%;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 5px;
          font-size: 16px;
        }

        input:focus, select:focus {
          outline: none;
          border-color: #007bff;
        }

        .connect-button {
          width: 100%;
          padding: 12px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 5px;
          font-size: 18px;
          font-weight: bold;
          cursor: pointer;
          transition: background 0.3s;
        }

        .connect-button:hover {
          background: #0056b3;
        }

        .connect-button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        .redirect-uri-container {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 5px;
          margin-bottom: 20px;
        }

        .input-with-copy {
          display: flex;
          gap: 10px;
        }

        .redirect-uri-input {
          flex: 1;
          background: white;
        }

        .copy-button {
          padding: 10px 15px;
          background: #28a745;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
        }

        .help-text {
          color: #856404;
          background: #fff3cd;
          padding: 10px;
          border-radius: 5px;
          margin-top: 10px;
          font-size: 14px;
        }

        .instructions {
          margin-top: 30px;
          padding-top: 20px;
          border-top: 1px solid #eee;
        }

        .instructions h3 {
          color: #333;
          margin-bottom: 15px;
        }

        .instructions ol {
          color: #666;
          line-height: 1.8;
        }

        .instructions a {
          color: #007bff;
          text-decoration: none;
        }

        .instructions a:hover {
          text-decoration: underline;
        }
      `}</style>
    </div>
  );
};

export default ConnectStore;