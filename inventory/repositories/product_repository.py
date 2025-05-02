from sqlalchemy.exc import SQLAlchemyError
from ..models import Product
from .base_repository import BaseRepository

class ProductRepository(BaseRepository):
    """Repository for Product model"""
    
    def __init__(self, session):
        super().__init__(session, Product)
    
    def get_by_barcode(self, barcode):
        """Get a product by its barcode"""
        return self.session.query(Product).filter(Product.barcode == barcode).first()
    
    def search_by_name(self, name_part):
        """Search products by name (partial match)"""
        return self.session.query(Product).filter(
            Product.name.ilike(f"%{name_part}%")
        ).all()
    
    def get_products_by_category(self, category_id):
        """Get all products in a specific category"""
        return self.session.query(Product).filter(
            Product.category_id == category_id
        ).all()