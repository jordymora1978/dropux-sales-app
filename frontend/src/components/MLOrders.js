import React, { useState, useEffect } from 'react';
import { ShoppingCart, Calendar, DollarSign, User, Package, ExternalLink, RefreshCw, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import apiService from '../services/api';

const MLOrders = ({ store }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    if (store) {
      loadOrders();
      loadUserInfo();
    }
  }, [store]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.request(`/api/ml/stores/${store.id}/orders`);
      setOrders(response.orders || []);
    } catch (error) {
      console.error('Error loading ML orders:', error);
      setError(error.message || 'Error al cargar las órdenes');
    } finally {
      setLoading(false);
    }
  };

  const loadUserInfo = async () => {
    try {
      const response = await apiService.request(`/api/ml/stores/${store.id}/user-info`);
      setUserInfo(response);
    } catch (error) {
      console.error('Error loading user info:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadOrders();
    setRefreshing(false);
  };

  const formatCurrency = (amount, currencyId = 'COP') => {
    const formatters = {
      COP: new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }),
      CLP: new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }),
      PEN: new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }),
    };
    return formatters[currencyId]?.format(amount) || `$${amount.toLocaleString()}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const badges = {
      confirmed: { class: 'status-confirmed', text: 'Confirmado', icon: CheckCircle },
      payment_required: { class: 'status-pending', text: 'Pago Pendiente', icon: Clock },
      payment_in_process: { class: 'status-processing', text: 'Procesando Pago', icon: Clock },
      paid: { class: 'status-paid', text: 'Pagado', icon: CheckCircle },
      shipped: { class: 'status-shipped', text: 'Enviado', icon: Package },
      delivered: { class: 'status-delivered', text: 'Entregado', icon: CheckCircle },
      cancelled: { class: 'status-cancelled', text: 'Cancelado', icon: AlertCircle }
    };
    return badges[status] || { class: 'status-unknown', text: status, icon: AlertCircle };
  };

  if (loading) {
    return (
      <div className="ml-orders-loading">
        <RefreshCw className="animate-spin" size={32} />
        <p>Cargando órdenes de MercadoLibre...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ml-orders-error">
        <AlertCircle size={48} />
        <h3>Error al cargar las órdenes</h3>
        <p>{error}</p>
        <button onClick={loadOrders} className="retry-btn">
          <RefreshCw size={16} />
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="ml-orders-container">
      {/* Header with store info */}
      <div className="ml-orders-header">
        <div className="store-info">
          <h2>Órdenes de MercadoLibre</h2>
          <div className="store-details">
            <span className="store-name">{store.store_name}</span>
            <span className="store-site">({store.site_name})</span>
            {userInfo && (
              <span className="store-nickname">@{userInfo.nickname}</span>
            )}
          </div>
        </div>
        <div className="orders-actions">
          <button 
            onClick={handleRefresh} 
            disabled={refreshing}
            className="refresh-btn"
          >
            <RefreshCw className={refreshing ? 'animate-spin' : ''} size={16} />
            {refreshing ? 'Actualizando...' : 'Actualizar'}
          </button>
        </div>
      </div>

      {/* User info summary */}
      {userInfo && (
        <div className="user-info-summary">
          <div className="info-item">
            <User size={16} />
            <span>Usuario ML: {userInfo.nickname}</span>
          </div>
          <div className="info-item">
            <Package size={16} />
            <span>Reputación: {userInfo.reputation?.level_id || 'N/A'}</span>
          </div>
          <div className="info-item">
            <DollarSign size={16} />
            <span>País: {userInfo.country_id}</span>
          </div>
        </div>
      )}

      {/* Orders stats */}
      <div className="orders-stats">
        <div className="stat-item">
          <div className="stat-number">{orders.length}</div>
          <div className="stat-label">Total Órdenes</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">
            {orders.filter(order => order.status === 'paid').length}
          </div>
          <div className="stat-label">Pagadas</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">
            {orders.filter(order => order.status === 'shipped').length}
          </div>
          <div className="stat-label">Enviadas</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">
            {formatCurrency(
              orders.reduce((total, order) => total + order.total_amount, 0),
              orders[0]?.currency_id
            )}
          </div>
          <div className="stat-label">Valor Total</div>
        </div>
      </div>

      {/* Orders list */}
      {orders.length === 0 ? (
        <div className="no-orders">
          <ShoppingCart size={64} />
          <h3>No hay órdenes disponibles</h3>
          <p>Esta tienda no tiene órdenes recientes o no se han sincronizado aún.</p>
        </div>
      ) : (
        <div className="orders-list">
          {orders.map((order) => {
            const statusBadge = getStatusBadge(order.status);
            const StatusIcon = statusBadge.icon;
            
            return (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <div className="order-id">
                    <ShoppingCart size={16} />
                    {order.id}
                  </div>
                  <div className={`order-status ${statusBadge.class}`}>
                    <StatusIcon size={14} />
                    {statusBadge.text}
                  </div>
                </div>

                <div className="order-content">
                  <div className="order-customer">
                    <h4>Cliente: {order.buyer_nickname}</h4>
                    <p>ID: {order.buyer_id}</p>
                  </div>

                  <div className="order-amount">
                    <div className="amount-main">
                      {formatCurrency(order.total_amount, order.currency_id)}
                    </div>
                    <div className="amount-currency">{order.currency_id}</div>
                  </div>

                  <div className="order-dates">
                    <div className="date-item">
                      <Calendar size={14} />
                      <span>Creada: {formatDate(order.date_created)}</span>
                    </div>
                    {order.date_closed && (
                      <div className="date-item">
                        <CheckCircle size={14} />
                        <span>Cerrada: {formatDate(order.date_closed)}</span>
                      </div>
                    )}
                  </div>

                  <div className="order-items">
                    <h5>Productos ({order.order_items?.length || 0})</h5>
                    {order.order_items?.slice(0, 2).map((item, index) => (
                      <div key={index} className="order-item">
                        <span className="item-title">{item.item?.title || 'Producto'}</span>
                        <span className="item-qty">Qty: {item.quantity}</span>
                        <span className="item-price">
                          {formatCurrency(item.unit_price, order.currency_id)}
                        </span>
                      </div>
                    ))}
                    {order.order_items?.length > 2 && (
                      <div className="more-items">
                        +{order.order_items.length - 2} productos más
                      </div>
                    )}
                  </div>

                  {order.shipping && (
                    <div className="order-shipping">
                      <h5>Envío</h5>
                      <p>Método: {order.shipping.shipping_option?.name || 'N/A'}</p>
                      <p>Costo: {formatCurrency(order.shipping.shipping_option?.cost || 0, order.currency_id)}</p>
                    </div>
                  )}
                </div>

                <div className="order-actions">
                  <button className="action-btn primary">
                    <ExternalLink size={14} />
                    Ver en ML
                  </button>
                  <button className="action-btn secondary">
                    Ver Detalles
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MLOrders;