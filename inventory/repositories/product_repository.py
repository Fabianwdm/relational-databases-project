from sqlalchemy.exc import SQLAlchemyError
from ..models import Product
from .base_repository import BaseRepository

class ProductRepository(BaseRepository):
    
    def __init__(self, session):
        super().__init__(session, Product)
    
    def get_by_barcode(self, barcode):
        return self.session.query(Product).filter(Product.barcode == barcode).first()
    
    def search_by_name(self, name_part):
        return self.session.query(Product).filter(
            Product.name.ilike(f"%{name_part}%")
        ).all()
    
    def get_products_by_category(self, category_id):
        return self.session.query(Product).filter(
            Product.category_id == category_id
        ).all()