from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from .base import Base

class Warehouse(Base):
    __tablename__ = 'warehouses'
    
    warehouse_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200))
    capacity = Column(Integer)
    status = Column(Enum('active', 'inactive', 'maintenance', name='warehouse_status'), default='active')
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="warehouse")
    transactions = relationship("Transaction", back_populates="warehouse")
    
    def __repr__(self):
        return f"<Warehouse(warehouse_id={self.warehouse_id}, name='{self.name}', status='{self.status}')>"