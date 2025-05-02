from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True)
    barcode = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    inventory_items = relationship("Inventory", back_populates="product")
    transactions = relationship("Transaction", back_populates="product")
    suppliers = relationship("ProductSupplier", back_populates="product")
    inventory_items = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(product_id={self.product_id}, barcode='{self.barcode}', name='{self.name}')>"