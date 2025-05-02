from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from ..models import Inventory, Product, Warehouse
from .base_repository import BaseRepository

class InventoryRepository(BaseRepository):
    
    def __init__(self, session):
        super().__init__(session, Inventory)
    
    def get_by_product_warehouse(self, product_id, warehouse_id):
        return self.session.query(Inventory).filter(
            and_(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id
            )
        ).first()
    
    def get_by_barcode_warehouse(self, barcode, warehouse_id):
        return self.session.query(Inventory).join(Product).filter(
            and_(
                Product.barcode == barcode,
                Inventory.warehouse_id == warehouse_id
            )
        ).first()
    
    def get_warehouse_inventory(self, warehouse_id):
        return (self.session.query(Inventory, Product)
                .join(Product)
                .filter(Inventory.warehouse_id == warehouse_id)
                .all())
    
    def get_low_stock_items(self, threshold=None):
        query = self.session.query(Inventory, Product, Warehouse).join(Product).join(Warehouse)
        
        if threshold is not None:
            query = query.filter(Inventory.quantity < threshold)
        else:
            query = query.filter(Inventory.quantity < Inventory.minimum_stock)
            
        return query.all()
    
    def update_quantity(self, product_id, warehouse_id, quantity_change):
        try:
            inventory_item = self.get_by_product_warehouse(product_id, warehouse_id)
            
            if inventory_item:
                inventory_item.quantity += quantity_change
                self.session.commit()
                return inventory_item
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e