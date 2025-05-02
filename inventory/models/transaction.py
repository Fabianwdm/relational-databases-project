from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.warehouse_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    quantity = Column(Float, nullable=False)
    transaction_type = Column(Enum('check-in', 'check-out', 'transfer-in', 'transfer-out', name='transaction_type'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(500))
    
    # Relationships
    product = relationship("Product", back_populates="transactions")
    warehouse = relationship("Warehouse", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, type='{self.transaction_type}', product_id={self.product_id}, quantity={self.quantity})>"