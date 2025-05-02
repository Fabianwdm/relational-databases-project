from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from ..models import Inventory, Product, Warehouse
from .base_repository import BaseRepository

class InventoryRepository(BaseRepository):
    """Repository for Inventory model"""
    
    def __init__(self, session):
        super().__init__(session, Inventory)
    
    def get_by_product_warehouse(self, product_id, warehouse_id):
        """Get inventory item by product_id and warehouse_id"""
        return self.session.query(Inventory).filter(
            and_(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id
            )
        ).first()
    
    def get_by_barcode_warehouse(self, barcode, warehouse_id):
        """Get inventory item by product barcode and warehouse_id"""
        return self.session.query(Inventory).join(Product).filter(
            and_(
                Product.barcode == barcode,
                Inventory.warehouse_id == warehouse_id
            )
        ).first()
    
    def get_warehouse_inventory(self, warehouse_id):
        """Get all inventory items in a specific warehouse with product details"""
        return (self.session.query(Inventory, Product)
                .join(Product)
                .filter(Inventory.warehouse_id == warehouse_id)
                .all())
    
    def get_low_stock_items(self, threshold=None):
        """Get items where quantity is below minimum_stock or optional threshold"""
        query = self.session.query(Inventory, Product, Warehouse).join(Product).join(Warehouse)
        
        if threshold is not None:
            query = query.filter(Inventory.quantity < threshold)
        else:
            query = query.filter(Inventory.quantity < Inventory.minimum_stock)
            
        return query.all()
    
    def update_quantity(self, product_id, warehouse_id, quantity_change):
        """Update inventory quantity by adding quantity_change (can be negative)"""
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