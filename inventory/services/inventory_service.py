from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from ..repositories import InventoryRepository, ProductRepository, TransactionRepository
from ..models import Inventory, Transaction

class InventoryService:
    
    def __init__(self, session):
        self.inventory_repo = InventoryRepository(session)
        self.product_repo = ProductRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.session = session
    
    def check_in(self, barcode, warehouse_id, quantity, user_id, notes=None):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        
        # Find product by barcode
        product = self.product_repo.get_by_barcode(barcode)
        if not product:
            raise ValueError(f"Product with barcode '{barcode}' not found")
        
        try:
            # Begin transaction
            self.session.begin_nested()
            
            # Get or create inventory item
            inventory_item = self.inventory_repo.get_by_product_warehouse(
                product.product_id, warehouse_id
            )
            
            if inventory_item:
                # Update existing inventory
                inventory_item = self.inventory_repo.update_quantity(
                    product.product_id, warehouse_id, quantity
                )
            else:
                # Create new inventory record
                inventory_item = self.inventory_repo.create(
                    product_id=product.product_id,
                    warehouse_id=warehouse_id,
                    quantity=quantity,
                    minimum_stock=0,
                    last_checked=datetime.utcnow()
                )
            
            # Record transaction
            transaction = self.transaction_repo.create(
                product_id=product.product_id,
                warehouse_id=warehouse_id,
                user_id=user_id,
                quantity=quantity,
                transaction_type='check-in',
                notes=notes
            )
            
            # Commit transaction
            self.session.commit()
            return inventory_item, transaction
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def check_out(self, barcode, warehouse_id, quantity, user_id, notes=None):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        
        # Find product by barcode
        product = self.product_repo.get_by_barcode(barcode)
        if not product:
            raise ValueError(f"Product with barcode '{barcode}' not found")
        
        # Find inventory item
        inventory_item = self.inventory_repo.get_by_product_warehouse(
            product.product_id, warehouse_id
        )
        
        if not inventory_item:
            raise ValueError(f"Product '{product.name}' not found in the specified warehouse")
        
        if inventory_item.quantity < quantity:
            raise ValueError(f"Insufficient quantity available. Current stock: {inventory_item.quantity}")
        
        try:
            # Begin transaction
            self.session.begin_nested()
            
            # Update inventory
            inventory_item = self.inventory_repo.update_quantity(
                product.product_id, warehouse_id, -quantity
            )
            
            # Record transaction
            transaction = self.transaction_repo.create(
                product_id=product.product_id,
                warehouse_id=warehouse_id,
                user_id=user_id,
                quantity=quantity,
                transaction_type='check-out',
                notes=notes
            )
            
            # Commit transaction
            self.session.commit()
            return inventory_item, transaction
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def transfer(self, barcode, from_warehouse_id, to_warehouse_id, quantity, user_id, notes=None):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        
        if from_warehouse_id == to_warehouse_id:
            raise ValueError("Source and destination warehouses must be different")
        
        # Find product by barcode
        product = self.product_repo.get_by_barcode(barcode)
        if not product:
            raise ValueError(f"Product with barcode '{barcode}' not found")
        
        # Find source inventory item
        source_item = self.inventory_repo.get_by_product_warehouse(
            product.product_id, from_warehouse_id
        )
        
        if not source_item:
            raise ValueError(f"Product '{product.name}' not found in the source warehouse")
        
        if source_item.quantity < quantity:
            raise ValueError(f"Insufficient quantity available. Current stock: {source_item.quantity}")
        
        try:
            # Begin transaction
            self.session.begin_nested()
            
            # Get or create destination inventory item
            dest_item = self.inventory_repo.get_by_product_warehouse(
                product.product_id, to_warehouse_id
            )
            
            if not dest_item:
                # Create new inventory record in destination warehouse
                dest_item = self.inventory_repo.create(
                    product_id=product.product_id,
                    warehouse_id=to_warehouse_id,
                    quantity=0,
                    minimum_stock=0,
                    last_checked=datetime.utcnow()
                )
            
            # Update source inventory
            source_item = self.inventory_repo.update_quantity(
                product.product_id, from_warehouse_id, -quantity
            )
            
            # Update destination inventory
            dest_item = self.inventory_repo.update_quantity(
                product.product_id, to_warehouse_id, quantity
            )
            
            # Record outgoing transaction
            out_transaction = self.transaction_repo.create(
                product_id=product.product_id,
                warehouse_id=from_warehouse_id,
                user_id=user_id,
                quantity=quantity,
                transaction_type='transfer-out',
                notes=f"Transfer to Warehouse #{to_warehouse_id}" + (f": {notes}" if notes else "")
            )
            
            # Record incoming transaction
            in_transaction = self.transaction_repo.create(
                product_id=product.product_id,
                warehouse_id=to_warehouse_id,
                user_id=user_id,
                quantity=quantity,
                transaction_type='transfer-in',
                notes=f"Transfer from Warehouse #{from_warehouse_id}" + (f": {notes}" if notes else "")
            )
            
            # Commit transaction
            self.session.commit()
            return source_item, dest_item, out_transaction, in_transaction
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def get_warehouse_inventory(self, warehouse_id):
        return self.inventory_repo.get_warehouse_inventory(warehouse_id)
    
    def get_low_stock_items(self, threshold=None):
        return self.inventory_repo.get_low_stock_items(threshold)
    
    def update_minimum_stock(self, product_id, warehouse_id, minimum_stock):
        inventory_item = self.inventory_repo.get_by_product_warehouse(product_id, warehouse_id)
        if not inventory_item:
            raise ValueError("Inventory item not found")
        return self.inventory_repo.update(inventory_item.inventory_id, minimum_stock=minimum_stock)
    