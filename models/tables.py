"""
SQLAlchemy table definitions for the sales system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Company(Base):
    """Empresas/Cuentas del sistema (multi-tenant)"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True)  # subdominio.drapify.com
    plan = Column(String(50), default="free")  # free, basic, premium
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="company")
    ml_accounts = relationship("MLAccount", back_populates="company")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="operator")  # master_admin, admin, operator, viewer
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    ml_accounts = relationship("MLAccount", back_populates="user")

class MLAccount(Base):
    __tablename__ = "ml_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    site_id = Column(String(10), nullable=False)  # MCO, MLC, MPE, CBT
    ml_user_id = Column(String(50))  # ID de usuario en MercadoLibre
    access_token = Column(Text)
    refresh_token = Column(Text)
    nickname = Column(String(255), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="ml_accounts")
    user = relationship("User", back_populates="ml_accounts")
    orders = relationship("MLOrder", back_populates="account")

class MLOrder(Base):
    __tablename__ = "ml_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(255), unique=True, index=True, nullable=False)
    account_id = Column(Integer, ForeignKey("ml_accounts.id"), nullable=False)
    buyer_data = Column(JSON)  # Store buyer information as JSON
    items = Column(JSON)  # Store order items as JSON
    status = Column(String(50), nullable=False)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    account = relationship("MLAccount", back_populates="orders")
    shipments = relationship("Shipment", back_populates="order")

class LogisticsProvider(Base):
    __tablename__ = "logistics_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # "Anicam", "Chilexpress", etc.
    api_endpoint = Column(String(255), nullable=False)
    credentials = Column(JSON)  # Store API credentials as JSON
    
    # Relationships
    shipments = relationship("Shipment", back_populates="provider")

class Shipment(Base):
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("ml_orders.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("logistics_providers.id"), nullable=False)
    tracking_number = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # "pending", "in_transit", "delivered", etc.
    
    # Relationships
    order = relationship("MLOrder", back_populates="shipments")
    provider = relationship("LogisticsProvider", back_populates="shipments")

# Additional tables for existing functionality
class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    telefono = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Venta(Base):
    __tablename__ = "ventas"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    producto = Column(String(255), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    descuento = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    estado = Column(String(50), default="pendiente")
    
    # Relationships
    cliente = relationship("Cliente")