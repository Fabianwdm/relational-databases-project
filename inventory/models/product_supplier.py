from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class ProductSupplier(Base):
    __tablename__ = 'product_suppliers'
    
    product_supplier_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.supplier_id'), nullable=False)
    lead_time = Column(Integer)  # In days
    price = Column(Float)
    
    # Relationships
    product = relationship("Product", back_populates="suppliers")
    supplier = relationship("Supplier", back_populates="products")
    
    # Ensure product can only be once per supplier
    __table_args__ = (
        UniqueConstraint('product_id', 'supplier_id', name='uix_product_supplier'),
    )
    
    def __repr__(self):
        return f"<ProductSupplier(product_id={self.product_id}, supplier_id={self.supplier_id}, price={self.price})>"