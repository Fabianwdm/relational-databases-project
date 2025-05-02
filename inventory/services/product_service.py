from ..repositories import ProductRepository
from ..models import Product

class ProductService:
    
    def __init__(self, session):
        self.product_repo = ProductRepository(session)
        self.session = session
    
    def get_all_products(self):
        return self.product_repo.get_all()
    
    def get_product_by_id(self, product_id):
        return self.product_repo.get_by_id(product_id)
    
    def get_product_by_barcode(self, barcode):
        return self.product_repo.get_by_barcode(barcode)
    
    def create_product(self, barcode, name, price, category_id=None, description=None):
        # Check if barcode already exists
        if self.product_repo.get_by_barcode(barcode):
            raise ValueError(f"Product with barcode '{barcode}' already exists")
        
        return self.product_repo.create(
            barcode=barcode,
            name=name,
            description=description,
            category_id=category_id,
            price=price
        )
    
    def update_product(self, product_id, **kwargs):
        # Check if barcode is being updated and already exists
        if 'barcode' in kwargs:
            existing = self.product_repo.get_by_barcode(kwargs['barcode'])
            if existing and existing.product_id != product_id:
                raise ValueError(f"Product with barcode '{kwargs['barcode']}' already exists")
        
        return self.product_repo.update(product_id, **kwargs)
    
    def delete_product(self, product_id):
        return self.product_repo.delete(product_id)
    
    def search_products(self, name=None, barcode=None, category_id=None):
        if barcode:
            product = self.product_repo.get_by_barcode(barcode)
            return [product] if product else []
        
        if name:
            return self.product_repo.search_by_name(name)
        
        if category_id:
            return self.product_repo.get_products_by_category(category_id)
        
        return []