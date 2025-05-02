from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    supplier_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(50))
    address = Column(String(200))
    
    # Relationships
    products = relationship("ProductSupplier", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier(supplier_id={self.supplier_id}, name='{self.name}')>"