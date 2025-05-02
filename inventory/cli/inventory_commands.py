from datetime import datetime
from ..services import InventoryService, ProductService

class InventoryCommands:
    """Commands for inventory operations"""
    
    def __init__(self, session, auth_commands):
        self.inventory_service = InventoryService(session)
        self.product_service = ProductService(session)
        self.auth_commands = auth_commands
    
    def check_in(self, args):
        """Check in products to warehouse"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        try:
            # Process check-in
            inventory_item, transaction = self.inventory_service.check_in(
                barcode=args.barcode,
                warehouse_id=args.warehouse,
                quantity=args.quantity,
                user_id=current_user.user_id,
                notes=args.notes
            )
            
            product = self.product_service.get_product_by_id(inventory_item.product_id)
            print(f"Successfully checked in {args.quantity} units of {product.name}")
            print(f"Current stock in warehouse {args.warehouse}: {inventory_item.quantity}")
            
            return True
        except ValueError as e:
            print(f"Error: {str(e)}")
            return False
    
    def check_out(self, args):
        """Check out products from warehouse"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        try:
            # Process check-out
            inventory_item, transaction = self.inventory_service.check_out(
                barcode=args.barcode,
                warehouse_id=args.warehouse,
                quantity=args.quantity,
                user_id=current_user.user_id,
                notes=args.notes
            )
            
            product = self.product_service.get_product_by_id(inventory_item.product_id)
            print(f"Successfully checked out {args.quantity} units of {product.name}")
            print(f"Current stock in warehouse {args.warehouse}: {inventory_item.quantity}")
            
            return True
        except ValueError as e:
            print(f"Error: {str(e)}")
            return False
    
    def transfer(self, args):
        """Transfer products between warehouses"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        try:
            # Process transfer
            source_item, dest_item, _, _ = self.inventory_service.transfer(
                barcode=args.barcode,
                from_warehouse_id=args.from_warehouse,
                to_warehouse_id=args.to_warehouse,
                quantity=args.quantity,
                user_id=current_user.user_id,
                notes=args.notes
            )
            
            product = self.product_service.get_product_by_id(source_item.product_id)
            print(f"Successfully transferred {args.quantity} units of {product.name}")
            print(f"Current stock in source warehouse {args.from_warehouse}: {source_item.quantity}")
            print(f"Current stock in destination warehouse {args.to_warehouse}: {dest_item.quantity}")
            
            return True
        except ValueError as e:
            print(f"Error: {str(e)}")
            return False