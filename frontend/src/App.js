import React, { useState, useEffect } from 'react';
import { User, Package, Truck, Eye, MessageSquare, ExternalLink, Sun, Moon, ShoppingCart, Users, Settings, BarChart3, X, Send, HelpCircle, MapPin, FileText, Clipboard, Edit3, Save } from 'lucide-react';
import './App.css';
import Login from './components/Login';
import apiService from './services/api';

const SalesDashboard = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      if (apiService.isAuthenticated()) {
        const userData = await apiService.verifyToken();
        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (response) => {
    setUser(response.user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    apiService.logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Cargando...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }
  const [theme, setTheme] = useState('light');
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  // const [currentPage, setCurrentPage] = useState(1); // Comentado temporalmente
  const [activeTab, setActiveTab] = useState('orders');
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [modalTab, setModalTab] = useState('messages');
  const [messageInput, setMessageInput] = useState('');
  const [isEditingPublication, setIsEditingPublication] = useState(false);
  // const [publicationData, setPublicationData] = useState({}); // Comentado temporalmente

  // Datos de ejemplo para el dashboard
  const mockOrders = [
    {
      id: 'MCO-2025001',
      marketplaceBadge: 'colombia',
      productImage: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=80&h=80&fit=crop',
      sku: 'B08NP2DYQR',
      productTitle: 'Auriculares Bluetooth Inalámbricos con Cancelación de Ruido Premium',
      mercadoLibreLink: 'https://articulo.mercadolibre.com.co/MCO-123456789-auriculares-bluetooth-inalambricos-cancelacion-ruido-premium',
      status: 'pending',
      shippingStatus: 'processing',
      customerName: 'María González',
      customerDocument: 'CC 9012051577',
      price: 189500,
      commission: 28425,
      netAmount: 161075,
      amazonDate: '2025-01-15',
      amazonPrice: 89.99,
      amazonLink: 'https://amazon.com/dp/B08NP2DYQR',
      amazonGSS: true,
      minutesAgo: 15,
      quantity: 1,
      dateCreated: '2025-01-15 14:30:00'
    },
    {
      id: 'MLC-2025002',
      marketplaceBadge: 'chile',
      productImage: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=80&h=80&fit=crop',
      sku: 'B07XQXZXVZ',
      productTitle: 'Zapatillas Deportivas Running Nike Air Max Revolution 5',
      mercadoLibreLink: 'https://articulo.mercadolibre.cl/MLC-987654321-zapatillas-deportivas-running-nike-air-max-revolution-5',
      status: 'approved',
      shippingStatus: 'shipped',
      customerName: 'Carlos Mendoza',
      customerDocument: 'RUT 105099282',
      customerPhone: '+56 9 8765 4321',
      customerEmail: 'carlos.mendoza@email.com',
      price: 89990,
      commission: 13498,
      netAmount: 76492,
      amazonDate: '2025-01-14',
      amazonPrice: 129.99,
      amazonLink: 'https://amazon.com/dp/B07XQXZXVZ',
      amazonGSS: false,
      minutesAgo: 45,
      quantity: 1,
      dateCreated: '2025-01-15 13:45:00'
    },
    {
      id: 'MPE-2025003',
      marketplaceBadge: 'peru',
      productImage: 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=80&h=80&fit=crop',
      sku: 'B09KMVXT7W',
      productTitle: 'Cámara Fotográfica Digital Canon EOS Rebel T100 Kit Completo',
      mercadoLibreLink: 'https://articulo.mercadolibre.com.pe/MPE-555666777-camara-fotografica-digital-canon-eos-rebel-t100-kit-completo',
      status: 'processing',
      shippingStatus: 'pending',
      customerName: 'Ana Rodríguez',
      customerDocument: 'DNI 42722765',
      customerPhone: '+51 987 654 321',
      customerEmail: 'ana.rodriguez@email.com',
      price: 1850,
      commission: 277.5,
      netAmount: 1572.5,
      amazonDate: '2025-01-13',
      amazonPrice: 599.99,
      amazonLink: 'https://amazon.com/dp/B09KMVXT7W',
      amazonGSS: true,
      minutesAgo: 120,
      quantity: 1,
      dateCreated: '2025-01-15 12:30:00'
    },
    {
      id: 'MCO-2025004',
      marketplaceBadge: 'colombia',
      productImage: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=80&h=80&fit=crop',
      sku: 'B08Z7GQXM2',
      productTitle: 'Smart Watch Deportivo con Monitor de Frecuencia Cardíaca',
      mercadoLibreLink: 'https://articulo.mercadolibre.com.co/MCO-444555666-smart-watch-deportivo-monitor-frecuencia-cardiaca',
      status: 'shipped',
      shippingStatus: 'shipped',
      customerName: 'Luis Pérez',
      customerDocument: 'CC 8901234567',
      customerPhone: '+57 301 987 6543',
      customerEmail: 'luis.perez@email.com',
      price: 125000,
      commission: 18750,
      netAmount: 106250,
      amazonDate: '2025-01-12',
      amazonPrice: 59.99,
      amazonLink: 'https://amazon.com/dp/B08Z7GQXM2',
      amazonGSS: true,
      minutesAgo: 180,
      quantity: 2,
      dateCreated: '2025-01-15 11:30:00'
    }
  ];

  // Datos de ejemplo para el modal
  const mockMessages = {
    'MCO-2025001': [
      { id: 1, sender: 'customer', text: 'Hola, ¿cuando llegará mi pedido?', time: '10:30 AM', date: '2025-01-15' },
      { id: 2, sender: 'seller', text: 'Buenos días! Su pedido fue despachado hoy y llegará en 3-5 días hábiles.', time: '10:45 AM', date: '2025-01-15' },
      { id: 3, sender: 'customer', text: '¿Puedo rastrear el envío?', time: '11:00 AM', date: '2025-01-15' },
      { id: 4, sender: 'seller', text: 'Por supuesto! Le comparto el número de guía: ANI-CO-789456123', time: '11:15 AM', date: '2025-01-15' },
      { id: 5, sender: 'customer', text: 'Perfecto, muchas gracias!', time: '11:20 AM', date: '2025-01-15' }
    ],
    'MLC-2025002': [
      { id: 1, sender: 'customer', text: '¿El producto es original?', time: '09:00 AM', date: '2025-01-14' },
      { id: 2, sender: 'seller', text: 'Sí, todos nuestros productos son 100% originales con garantía.', time: '09:30 AM', date: '2025-01-14' },
      { id: 3, sender: 'customer', text: 'Excelente, ya realicé el pago', time: '10:00 AM', date: '2025-01-14' }
    ]
  };

  const mockQuestions = {
    'MCO-2025001': [
      { id: 1, question: '¿El producto incluye garantía?', answer: 'Sí, incluye garantía de 12 meses.', time: '2 días atrás', answered: true },
      { id: 2, question: '¿Es compatible con iPhone?', answer: 'Sí, es compatible con iPhone y Android.', time: '3 días atrás', answered: true },
      { id: 3, question: '¿Viene con estuche de carga?', answer: 'Pendiente de respuesta...', time: '5 horas atrás', answered: false }
    ],
    'MLC-2025002': [
      { id: 1, question: '¿Qué tallas tienen disponibles?', answer: 'Disponible en tallas 38-44.', time: '1 día atrás', answered: true },
      { id: 2, question: '¿El color es igual a la foto?', answer: 'Sí, los colores son exactos a las fotos.', time: '2 días atrás', answered: true }
    ]
  };

  const mockLogistics = {
    'MCO-2025001': {
      provider: 'ANICAM',
      tracking: 'ANI-CO-789456123',
      status: 'En tránsito',
      steps: [
        { status: 'Orden recibida', date: '2025-01-15 08:00', completed: true, location: 'Bogotá, Colombia' },
        { status: 'En centro de distribución', date: '2025-01-15 12:00', completed: true, location: 'Bogotá, Colombia' },
        { status: 'En camino', date: '2025-01-16 08:00', completed: true, location: 'Medellín, Colombia' },
        { status: 'En reparto', date: '2025-01-17 10:00', completed: false, location: 'Medellín, Colombia' },
        { status: 'Entregado', date: 'Estimado: 2025-01-18', completed: false, location: 'Destino final' }
      ]
    },
    'MLC-2025002': {
      provider: 'CHILEXPRESS',
      tracking: 'CHX-CL-456789321',
      status: 'Entregado',
      steps: [
        { status: 'Orden recibida', date: '2025-01-13 09:00', completed: true, location: 'Santiago, Chile' },
        { status: 'Procesado en bodega', date: '2025-01-13 14:00', completed: true, location: 'Santiago, Chile' },
        { status: 'En tránsito', date: '2025-01-14 08:00', completed: true, location: 'Valparaíso, Chile' },
        { status: 'En oficina de destino', date: '2025-01-14 16:00', completed: true, location: 'Valparaíso, Chile' },
        { status: 'Entregado', date: '2025-01-15 11:30', completed: true, location: 'Valparaíso, Chile' }
      ]
    },
    'MLM-2025003': {
      provider: 'ANICAM',
      tracking: 'ANI-PE-321654987',
      status: 'Procesando',
      steps: [
        { status: 'Orden recibida', date: '2025-01-15 10:00', completed: true, location: 'Lima, Perú' },
        { status: 'En preparación', date: '2025-01-15 14:00', completed: false, location: 'Lima, Perú' },
        { status: 'Listo para envío', date: 'Pendiente', completed: false, location: 'Lima, Perú' },
        { status: 'En tránsito', date: 'Pendiente', completed: false, location: '' },
        { status: 'Entregado', date: 'Pendiente', completed: false, location: '' }
      ]
    }
  };

  // Datos de ejemplo para publicaciones
  const mockPublications = {
    'MCO-2025001': {
      nombre: 'Auriculares Bluetooth Inalámbricos con Cancelación de Ruido Premium',
      precio: 189500,
      moneda: 'COP',
      tipoPublicacion: 'Premium',
      diasEntrega: '3-5 días hábiles',
      categoria: 'Electrónicos > Audio > Auriculares',
      estado: 'Activa',
      stock: 25,
      descripcion: 'Auriculares inalámbricos de alta calidad con tecnología de cancelación de ruido activa. Batería de larga duración hasta 30 horas. Sonido Hi-Fi con drivers de 40mm. Compatibles con iOS y Android.',
      plantilla: 'ELECTRONICA_PREMIUM',
      garantia: '12 meses',
      marca: 'TechSound Pro'
    },
    'MLC-2025002': {
      nombre: 'Zapatillas Deportivas Running Nike Air Max Revolution 5',
      precio: 89990,
      moneda: 'CLP',
      tipoPublicacion: 'Clásica',
      diasEntrega: '2-4 días hábiles',
      categoria: 'Deportes > Calzado > Running',
      estado: 'Activa',
      stock: 15,
      descripcion: 'Zapatillas Nike Air Max Revolution 5 para running. Tecnología Air Max para máxima comodidad. Suela de goma resistente. Diseño moderno y versátil.',
      plantilla: 'DEPORTES_STANDARD',
      garantia: '6 meses por defectos de fabricación',
      marca: 'Nike'
    },
    'MPE-2025003': {
      nombre: 'Cámara Fotográfica Digital Canon EOS Rebel T100 Kit Completo',
      precio: 1850,
      moneda: 'PEN',
      tipoPublicacion: 'Premium',
      diasEntrega: '5-7 días hábiles',
      categoria: 'Electrónicos > Cámaras > DSLR',
      estado: 'Activa',
      stock: 8,
      descripción: 'Cámara DSLR Canon EOS Rebel T100 con sensor APS-C de 18MP. Incluye lente 18-55mm, cargador, batería y correa. Video Full HD. Perfecta para principiantes.',
      plantilla: 'FOTOGRAFIA_PREMIUM',
      garantia: '24 meses',
      marca: 'Canon'
    }
  };

  // Datos de ejemplo para fichas técnicas
  const mockTechSpecs = {
    'MCO-2025001': {
      proveedor: 'TechSound International Ltd.',
      codigoProveedor: 'TSI-BT-5000',
      peso: '280 gramos',
      dimensiones: '17 x 19 x 8.5 cm',
      material: 'Plástico ABS + Metal + Espuma memory foam',
      color: 'Negro mate',
      conectividad: 'Bluetooth 5.0, USB-C, Jack 3.5mm',
      bateria: '1200mAh Li-ion, 30h reproducción',
      caracteristicas: [
        'Cancelación activa de ruido (ANC)',
        'Micrófono integrado para llamadas',
        'Control táctil inteligente',
        'Plegable para transporte',
        'Certificación IPX4 resistente al agua'
      ],
      contenidoCaja: 'Auriculares, Cable USB-C, Cable 3.5mm, Estuche de transporte, Manual',
      paisOrigen: 'China',
      certificaciones: 'FCC, CE, RoHS'
    },
    'MLC-2025002': {
      proveedor: 'Nike Sports Equipment Co.',
      codigoProveedor: 'NK-AMR5-2025',
      peso: '295 gramos (talla 42)',
      dimensiones: 'Tallas 38-46 disponibles',
      material: 'Upper: Mesh + sintético, Suela: Goma EVA',
      color: 'Negro/Blanco/Rojo',
      tecnologia: 'Nike Air Max, Zoom Air',
      genero: 'Unisex',
      caracteristicas: [
        'Amortiguación Air Max en talón',
        'Upper transpirable de mesh',
        'Suela antideslizante',
        'Soporte de arco reforzado',
        'Diseño ergonómico'
      ],
      contenidoCaja: 'Zapatillas, Cordones adicionales, Etiquetas',
      paisOrigen: 'Vietnam',
      tallaje: 'Talla normal, recomendamos talla habitual'
    },
    'MPE-2025003': {
      proveedor: 'Canon Imaging Solutions',
      codigoProveedor: 'CIS-T100-KIT',
      peso: '475 gramos (solo cuerpo)',
      dimensiones: '12.9 x 10.1 x 6.7 cm',
      sensor: 'APS-C CMOS 18 megapíxeles',
      procesador: 'DIGIC 4+',
      lente: 'EF-S 18-55mm f/3.5-5.6 IS II',
      pantalla: 'LCD 2.7" (6.8 cm)',
      caracteristicas: [
        'Modo automático inteligente',
        'Video Full HD 1080p',
        'WiFi integrado',
        '9 puntos de enfoque automático',
        'Modo retrato con desenfoque'
      ],
      contenidoCaja: 'Cámara T100, Lente 18-55mm, Batería LP-E10, Cargador, Correa, Manual',
      paisOrigen: 'Japón',
      formatosArchivo: 'JPEG, RAW (CR2), MP4'
    }
  };

  const stats = {
    pending: 23,
    processing: 15,
    shipped: 42,
    revenue: 2847650
  };

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const formatCurrency = (amount, country = 'colombia') => {
    const formatters = {
      colombia: new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }),
      chile: new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }),
      peru: new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }),
    };
    return formatters[country]?.format(amount) || `$${amount.toLocaleString()}`;
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { class: 'status-pending', text: 'Pendiente' },
      approved: { class: 'status-approved', text: 'Aprobado' },
      processing: { class: 'status-processing', text: 'Procesando' },
      shipped: { class: 'status-shipped', text: 'Enviado' }
    };
    return badges[status] || badges.pending;
  };

  const getMarketBadge = (market) => {
    const badges = {
      colombia: { class: 'market-colombia', text: 'Colombia' },
      chile: { class: 'market-chile', text: 'Chile' },
      peru: { class: 'market-peru', text: 'Perú' }
    };
    return badges[market] || badges.colombia;
  };

  const filteredOrders = mockOrders.filter(order => {
    const matchesFilter = activeFilter === 'all' || order.status === activeFilter;
    const matchesSearch = order.productTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         order.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         order.customerName.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className={`app-layout ${theme}-mode`}>
      {/* SIDEBAR */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">Drapify Sales</div>
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? <Moon size={14} /> : <Sun size={14} />}
            {theme === 'light' ? ' Modo Oscuro' : ' Modo Claro'}
          </button>
        </div>
        
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === 'orders' ? 'active' : ''}`}
            onClick={() => setActiveTab('orders')}
          >
            <ShoppingCart size={18} />
            Órdenes de Venta
          </button>
          <button 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <BarChart3 size={18} />
            Dashboard
          </button>
          <button 
            className={`nav-item ${activeTab === 'customers' ? 'active' : ''}`}
            onClick={() => setActiveTab('customers')}
          >
            <Users size={18} />
            Clientes
          </button>
          <button 
            className={`nav-item ${activeTab === 'products' ? 'active' : ''}`}
            onClick={() => setActiveTab('products')}
          >
            <Package size={18} />
            Productos
          </button>
          <button 
            className={`nav-item ${activeTab === 'logistics' ? 'active' : ''}`}
            onClick={() => setActiveTab('logistics')}
          >
            <Truck size={18} />
            Logística
          </button>
          <button 
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <Settings size={18} />
            Configuración
          </button>
        </nav>
      </div>

      {/* MAIN CONTENT */}
      <div className="main-content">
        {/* TOP HEADER */}
        <div className="top-header">
          <div className="header-left">
            <h1 className="page-title">Órdenes de Venta</h1>
            <div className="search-box">
              <input
                type="text"
                placeholder="Buscar por producto, SKU o cliente..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          
          <div className="header-right">
            <button 
              className={`filter-btn ${activeFilter === 'all' ? 'active' : ''}`}
              onClick={() => setActiveFilter('all')}
            >
              Todas
            </button>
            <button 
              className={`filter-btn ${activeFilter === 'pending' ? 'active' : ''}`}
              onClick={() => setActiveFilter('pending')}
            >
              Pendientes
            </button>
            <button 
              className={`filter-btn ${activeFilter === 'processing' ? 'active' : ''}`}
              onClick={() => setActiveFilter('processing')}
            >
              Procesando
            </button>
            <button 
              className={`filter-btn ${activeFilter === 'shipped' ? 'active' : ''}`}
              onClick={() => setActiveFilter('shipped')}
            >
              Enviadas
            </button>
            <div className="user-info">
              <User size={16} />
              {user?.email || 'Usuario'}
              <button 
                onClick={handleLogout}
                style={{ 
                  marginLeft: '10px', 
                  padding: '4px 8px', 
                  fontSize: '12px',
                  background: '#dc3545',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Salir
              </button>
            </div>
          </div>
        </div>

        {/* CONTENT AREA */}
        <div className="content-area">
          {/* STATS ROW */}
          <div className="stats-row">
            <div className="stat-card pending">
              <div className="stat-number">{stats.pending}</div>
              <div className="stat-label">Órdenes Pendientes</div>
            </div>
            <div className="stat-card processing">
              <div className="stat-number">{stats.processing}</div>
              <div className="stat-label">En Procesamiento</div>
            </div>
            <div className="stat-card shipped">
              <div className="stat-number">{stats.shipped}</div>
              <div className="stat-label">Enviadas Hoy</div>
            </div>
            <div className="stat-card revenue">
              <div className="stat-number">{formatCurrency(stats.revenue)}</div>
              <div className="stat-label">Ingresos del Mes</div>
            </div>
          </div>

          {/* ORDERS CONTAINER */}
          <div className="orders-container">
            <div className="orders-header">
              <div className="orders-title">Órdenes Recientes</div>
              <div className="orders-count">{filteredOrders.length} órdenes encontradas</div>
            </div>

            {/* ORDERS LIST */}
            {filteredOrders.map((order, index) => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <div>
                    <div className="order-id">{order.id}</div>
                    <div className="order-time">Hace {order.minutesAgo} minutos</div>
                  </div>
                  <div className={`market-badge ${getMarketBadge(order.marketplaceBadge).class}`}>
                    {getMarketBadge(order.marketplaceBadge).text}
                  </div>
                </div>

                <div className="order-content">
                  {/* PRODUCT IMAGE */}
                  <div className="product-image-container">
                    <img src={order.productImage} alt={order.productTitle} className="product-image" />
                    <div className="minutes-badge">{order.minutesAgo}m</div>
                  </div>

                  {/* ORDER DETAILS */}
                  <div className="order-details">
                    <h4>{order.id}</h4>
                    <div className="sku">{order.sku}</div>
                    <a 
                      href={order.mercadoLibreLink} 
                      className="product-title-link" 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      {order.productTitle}
                    </a>
                    <div className="status-badges">
                      <span className={`status-badge ${getStatusBadge(order.status).class}`}>
                        {getStatusBadge(order.status).text}
                      </span>
                      <span className={`status-badge ${getStatusBadge(order.shippingStatus).class}`}>
                        {getStatusBadge(order.shippingStatus).text}
                      </span>
                    </div>
                  </div>

                  {/* CUSTOMER INFO */}
                  <div className="customer-info">
                    <h5>{order.customerName}</h5>
                    <div className="customer-document">{order.customerDocument}</div>
                    <div className="shipping-badges-vertical">
                      <span className="status-badge status-processing">ANICAM</span>
                      <span className="status-badge status-shipped">CHILEXPRESS</span>
                      <span className="status-badge status-pending">PERALERTA</span>
                    </div>
                  </div>

                  {/* AMAZON INFO */}
                  <div className="amazon-info">
                    <div className="amazon-date">Comprado: {order.amazonDate}</div>
                    <div className="amazon-price">${order.amazonPrice} USD</div>
                    <a href={order.amazonLink} className="amazon-link" target="_blank" rel="noopener noreferrer">
                      Ver en Amazon <ExternalLink size={10} />
                    </a>
                    {order.amazonGSS && <span className="amazon-gss">GSS</span>}
                  </div>

                  {/* FINANCIAL INFO */}
                  <div className="financial-info">
                    <div className="price">{formatCurrency(order.price, order.marketplaceBadge)}</div>
                    <div className="commission">Comisión: {formatCurrency(order.commission, order.marketplaceBadge)}</div>
                    <div className="net-amount">Neto: {formatCurrency(order.netAmount, order.marketplaceBadge)}</div>
                  </div>

                  {/* ACTIONS */}
                  <div className="actions">
                    <button 
                      className="action-btn primary"
                      onClick={() => {
                        setSelectedOrder(order);
                        setShowMessageModal(true);
                        setModalTab('messages');
                      }}
                    >
                      <MessageSquare size={14} />
                      Mensaje
                    </button>
                    <button className="action-btn">
                      <Eye size={14} />
                      Ver Detalle
                    </button>
                    <button className="action-btn">
                      <Truck size={14} />
                      Tracking
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {/* PAGINATION */}
            <div className="pagination">
              <div className="pagination-info">
                Mostrando {filteredOrders.length} de {mockOrders.length} órdenes
              </div>
              <div className="pagination-controls">
                <button className="page-btn">‹</button>
                <button className="page-btn active">1</button>
                <button className="page-btn">2</button>
                <button className="page-btn">3</button>
                <button className="page-btn">›</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* MODAL DE MENSAJES */}
      {showMessageModal && selectedOrder && (
        <div className="modal-overlay" onClick={() => setShowMessageModal(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-order-info">
                <img 
                  src={selectedOrder.productImage} 
                  alt={selectedOrder.productTitle}
                  className="modal-product-image"
                />
                <div className="modal-order-details">
                  <div className="modal-order-title">{selectedOrder.productTitle}</div>
                  <div className="modal-order-meta">
                    <span className="modal-order-id">{selectedOrder.id}</span>
                    <span className={`modal-country-badge ${selectedOrder.marketplaceBadge}`}>
                      {getMarketBadge(selectedOrder.marketplaceBadge).text}
                    </span>
                  </div>
                </div>
              </div>
              <button className="modal-close" onClick={() => setShowMessageModal(false)}>
                <X size={20} />
              </button>
            </div>
            
            {/* TABS DEL MODAL */}
            <div className="modal-tabs">
              <button 
                className={`modal-tab ${modalTab === 'messages' ? 'active' : ''}`}
                onClick={() => setModalTab('messages')}
              >
                <MessageSquare size={16} />
                Mensajes
              </button>
              <button 
                className={`modal-tab ${modalTab === 'questions' ? 'active' : ''}`}
                onClick={() => setModalTab('questions')}
              >
                <HelpCircle size={16} />
                Preguntas
              </button>
              <button 
                className={`modal-tab ${modalTab === 'logistics' ? 'active' : ''}`}
                onClick={() => setModalTab('logistics')}
              >
                <Truck size={16} />
                Logística
              </button>
              <button 
                className={`modal-tab ${modalTab === 'publication' ? 'active' : ''}`}
                onClick={() => setModalTab('publication')}
              >
                <FileText size={16} />
                Publicación
              </button>
              <button 
                className={`modal-tab ${modalTab === 'techspecs' ? 'active' : ''}`}
                onClick={() => setModalTab('techspecs')}
              >
                <Clipboard size={16} />
                Ficha Técnica
              </button>
            </div>
            
            {/* CONTENIDO DEL MODAL */}
            <div className="modal-content">
              {/* TAB MENSAJES */}
              {modalTab === 'messages' && (
                <div className="messages-container">
                  <div className="messages-list">
                    {(mockMessages[selectedOrder.id] || []).map((message) => (
                      <div key={message.id} className={`message ${message.sender}`}>
                        <div className="message-bubble">
                          <p>{message.text}</p>
                          <span className="message-time">{message.time}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="message-input-container">
                    <input 
                      type="text"
                      placeholder="Escribe un mensaje..."
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      className="message-input"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          // Aquí enviarías el mensaje
                          setMessageInput('');
                        }
                      }}
                    />
                    <button className="send-button">
                      <Send size={18} />
                    </button>
                  </div>
                </div>
              )}
              
              {/* TAB PREGUNTAS */}
              {modalTab === 'questions' && (
                <div className="questions-container">
                  {(mockQuestions[selectedOrder.id] || []).map((q) => (
                    <div key={q.id} className="question-item">
                      <div className="question-header">
                        <HelpCircle size={16} className={q.answered ? 'answered' : 'pending'} />
                        <span className="question-time">{q.time}</span>
                      </div>
                      <div className="question-text">
                        <strong>P:</strong> {q.question}
                      </div>
                      <div className={`answer-text ${!q.answered ? 'pending' : ''}`}>
                        <strong>R:</strong> {q.answer}
                      </div>
                      {!q.answered && (
                        <button className="answer-button">Responder</button>
                      )}
                    </div>
                  ))}
                  {(!mockQuestions[selectedOrder.id] || mockQuestions[selectedOrder.id].length === 0) && (
                    <div className="no-questions">
                      <HelpCircle size={48} />
                      <p>No hay preguntas para esta orden</p>
                    </div>
                  )}
                </div>
              )}
              
              {/* TAB LOGÍSTICA */}
              {modalTab === 'logistics' && (
                <div className="logistics-container">
                  {mockLogistics[selectedOrder.id] ? (
                    <>
                      <div className="logistics-header">
                        <div className="logistics-provider">
                          <Truck size={20} />
                          <span className={`provider-badge ${mockLogistics[selectedOrder.id].provider.toLowerCase()}`}>
                            {mockLogistics[selectedOrder.id].provider}
                          </span>
                        </div>
                        <div className="tracking-info">
                          <span>Guía: {mockLogistics[selectedOrder.id].tracking}</span>
                          <span className="status-text">{mockLogistics[selectedOrder.id].status}</span>
                        </div>
                      </div>
                      
                      <div className="logistics-timeline">
                        {[...mockLogistics[selectedOrder.id].steps].reverse().map((step, index, array) => {
                          const originalIndex = array.length - 1 - index;
                          return (
                            <div key={originalIndex} className={`timeline-step ${step.completed ? 'completed' : ''}`}>
                              <div className="timeline-marker">
                                {step.completed ? '✓' : originalIndex + 1}
                              </div>
                              <div className="timeline-content">
                                <h4>{step.status}</h4>
                                <p className="timeline-date">{step.date}</p>
                                {step.location && (
                                  <p className="timeline-location">
                                    <MapPin size={12} /> {step.location}
                                  </p>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </>
                  ) : (
                    <div className="no-logistics">
                      <Package size={48} />
                      <p>Información de envío no disponible</p>
                      <span>La información de tracking estará disponible una vez procesado el envío</span>
                    </div>
                  )}
                </div>
              )}
              
              {/* TAB PUBLICACIÓN */}
              {modalTab === 'publication' && (
                <div className="publication-container">
                  {mockPublications[selectedOrder.id] ? (
                    <>
                      <div className="publication-header">
                        <div className="publication-title-section">
                          <h3>{mockPublications[selectedOrder.id].nombre}</h3>
                          <div className="publication-status">
                            <span className={`status-badge status-${mockPublications[selectedOrder.id].estado.toLowerCase()}`}>
                              {mockPublications[selectedOrder.id].estado}
                            </span>
                          </div>
                        </div>
                        <button 
                          className="edit-publication-btn"
                          onClick={() => setIsEditingPublication(!isEditingPublication)}
                        >
                          {isEditingPublication ? <Save size={16} /> : <Edit3 size={16} />}
                          {isEditingPublication ? 'Guardar' : 'Editar'}
                        </button>
                      </div>
                      
                      <div className="publication-content">
                        <div className="publication-row">
                          <div className="publication-field">
                            <label>Precio</label>
                            {isEditingPublication ? (
                              <input 
                                type="number" 
                                defaultValue={mockPublications[selectedOrder.id].precio}
                                className="publication-input"
                              />
                            ) : (
                              <span className="publication-value price">
                                {formatCurrency(mockPublications[selectedOrder.id].precio, selectedOrder.marketplaceBadge)}
                              </span>
                            )}
                          </div>
                          <div className="publication-field">
                            <label>Tipo de Publicación</label>
                            {isEditingPublication ? (
                              <select className="publication-select">
                                <option value="Premium">Premium</option>
                                <option value="Clásica">Clásica</option>
                                <option value="Gratuita">Gratuita</option>
                              </select>
                            ) : (
                              <span className="publication-value">{mockPublications[selectedOrder.id].tipoPublicacion}</span>
                            )}
                          </div>
                          <div className="publication-field">
                            <label>Días de Entrega</label>
                            {isEditingPublication ? (
                              <input 
                                type="text" 
                                defaultValue={mockPublications[selectedOrder.id].diasEntrega}
                                className="publication-input"
                              />
                            ) : (
                              <span className="publication-value">{mockPublications[selectedOrder.id].diasEntrega}</span>
                            )}
                          </div>
                        </div>
                        
                        <div className="publication-row">
                          <div className="publication-field">
                            <label>Categoría</label>
                            <span className="publication-value category">{mockPublications[selectedOrder.id].categoria}</span>
                          </div>
                          <div className="publication-field">
                            <label>Stock Disponible</label>
                            {isEditingPublication ? (
                              <input 
                                type="number" 
                                defaultValue={mockPublications[selectedOrder.id].stock}
                                className="publication-input"
                              />
                            ) : (
                              <span className="publication-value stock">{mockPublications[selectedOrder.id].stock} unidades</span>
                            )}
                          </div>
                          <div className="publication-field">
                            <label>Plantilla</label>
                            {isEditingPublication ? (
                              <select className="publication-select">
                                <option value="ELECTRONICA_PREMIUM">Electrónica Premium</option>
                                <option value="DEPORTES_STANDARD">Deportes Standard</option>
                                <option value="FOTOGRAFIA_PREMIUM">Fotografía Premium</option>
                              </select>
                            ) : (
                              <span className="publication-value template">{mockPublications[selectedOrder.id].plantilla}</span>
                            )}
                          </div>
                        </div>
                        
                        <div className="publication-field full-width">
                          <label>Descripción del Producto</label>
                          {isEditingPublication ? (
                            <textarea 
                              className="publication-textarea"
                              defaultValue={mockPublications[selectedOrder.id].descripcion}
                              rows="4"
                            />
                          ) : (
                            <div className="publication-description">
                              {mockPublications[selectedOrder.id].descripcion}
                            </div>
                          )}
                        </div>
                        
                        <div className="publication-row">
                          <div className="publication-field">
                            <label>Marca</label>
                            <span className="publication-value brand">{mockPublications[selectedOrder.id].marca}</span>
                          </div>
                          <div className="publication-field">
                            <label>Garantía</label>
                            <span className="publication-value warranty">{mockPublications[selectedOrder.id].garantia}</span>
                          </div>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="no-publication">
                      <FileText size={48} />
                      <p>Información de publicación no disponible</p>
                    </div>
                  )}
                </div>
              )}
              
              {/* TAB FICHA TÉCNICA */}
              {modalTab === 'techspecs' && (
                <div className="techspecs-container">
                  {mockTechSpecs[selectedOrder.id] ? (
                    <>
                      <div className="techspecs-header">
                        <h3>Especificaciones Técnicas</h3>
                        <div className="provider-info">
                          <span className="provider-label">Proveedor:</span>
                          <span className="provider-name">{mockTechSpecs[selectedOrder.id].proveedor}</span>
                        </div>
                      </div>
                      
                      <div className="techspecs-content">
                        <div className="techspecs-section">
                          <h4>Información General</h4>
                          <div className="techspecs-grid">
                            <div className="techspec-item">
                              <label>Código Proveedor</label>
                              <span>{mockTechSpecs[selectedOrder.id].codigoProveedor}</span>
                            </div>
                            <div className="techspec-item">
                              <label>Peso</label>
                              <span>{mockTechSpecs[selectedOrder.id].peso}</span>
                            </div>
                            <div className="techspec-item">
                              <label>Dimensiones</label>
                              <span>{mockTechSpecs[selectedOrder.id].dimensiones}</span>
                            </div>
                            <div className="techspec-item">
                              <label>País de Origen</label>
                              <span>{mockTechSpecs[selectedOrder.id].paisOrigen}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="techspecs-section">
                          <h4>Especificaciones</h4>
                          <div className="techspecs-grid">
                            {Object.entries(mockTechSpecs[selectedOrder.id])
                              .filter(([key]) => !['proveedor', 'codigoProveedor', 'peso', 'dimensiones', 'paisOrigen', 'caracteristicas', 'contenidoCaja'].includes(key))
                              .map(([key, value]) => (
                                <div key={key} className="techspec-item">
                                  <label>{key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}</label>
                                  <span>{value}</span>
                                </div>
                              ))
                            }
                          </div>
                        </div>
                        
                        <div className="techspecs-section">
                          <h4>Características Principales</h4>
                          <ul className="characteristics-list">
                            {mockTechSpecs[selectedOrder.id].caracteristicas.map((caracteristica, index) => (
                              <li key={index}>{caracteristica}</li>
                            ))}
                          </ul>
                        </div>
                        
                        <div className="techspecs-section">
                          <h4>Contenido de la Caja</h4>
                          <div className="box-content">
                            {mockTechSpecs[selectedOrder.id].contenidoCaja}
                          </div>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="no-techspecs">
                      <Clipboard size={48} />
                      <p>Ficha técnica no disponible</p>
                      <span>La información técnica estará disponible próximamente</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesDashboard;