from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Inventory(Base):
    __tablename__ = 'inventory'
    
    inventory_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.warehouse_id'), nullable=False)
    quantity = Column(Float, default=0)
    minimum_stock = Column(Float, default=0)
    last_checked = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    
    # Ensure product can only be once per warehouse
    __table_args__ = (
        UniqueConstraint('product_id', 'warehouse_id', name='uix_inventory_product_warehouse'),
    )
    
    def __repr__(self):
        return f"<Inventory(inventory_id={self.inventory_id}, product_id={self.product_id}, warehouse_id={self.warehouse_id}, quantity={self.quantity})>"