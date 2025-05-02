from ..services import ProductService
from ..utils.barcode_utils import validate_barcode, process_barcode_input, read_barcode_from_scanner
from ..models import Category

class ScanCommands:
    """Commands for barcode scanning operations"""
    
    def __init__(self, session, auth_commands):
        self.session = session
        self.auth_commands = auth_commands
        self.product_service = ProductService(session)
    
    def scan_and_add(self, args):
        """Interactive mode to scan barcodes and add products"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        # Check if user has sufficient permissions
        if current_user.role not in ['admin', 'manager']:
            print("Error: Insufficient permissions")
            return False
        
        print("\n=== Product Scan Mode ===")
        print("Scan a product barcode and enter details. Press Ctrl+C to exit.\n")
        
        try:
            while True:
                print("\nScanning new product:")
                barcode = read_barcode_from_scanner("Scan barcode: ")
                
                if not barcode:
                    print("Empty barcode detected. Exiting scan mode.")
                    break
                
                # Validate barcode format
                valid, error = validate_barcode(barcode)
                if not valid:
                    print(f"Invalid barcode: {error}")
                    continue
                
                # Check if barcode already exists
                existing_product = self.product_service.get_product_by_barcode(barcode)
                if existing_product:
                    print(f"Product with barcode '{barcode}' already exists:")
                    print(f"ID: {existing_product.product_id}, Name: {existing_product.name}, Price: ${existing_product.price:.2f}")
                    update = input("Do you want to update this product? (y/n): ").lower()
                    if update != 'y':
                        continue
                    
                    # Collect update information
                    print("\nEnter new product details (press Enter to keep current value):")
                    name = input(f"Product name [{existing_product.name}]: ")
                    name = name or existing_product.name
                    
                    price_str = input(f"Price [${existing_product.price:.2f}]: $")
                    if price_str:
                        try:
                            price = float(price_str)
                        except ValueError:
                            print("Invalid price format. Using current price.")
                            price = existing_product.price
                    else:
                        price = existing_product.price
                    
                    category_id = None
                    if args.show_categories:
                        self._list_categories()
                        cat_input = input(f"Category ID [{existing_product.category_id or 'None'}]: ")
                        if cat_input:
                            try:
                                category_id = int(cat_input)
                            except ValueError:
                                print("Invalid category ID. No category will be assigned.")
                    
                    description = input(f"Description [{existing_product.description or ''}]: ")
                    description = description or existing_product.description
                    
                    # Update the product
                    try:
                        update_data = {'name': name, 'price': price}
                        if category_id is not None:
                            update_data['category_id'] = category_id
                        if description:
                            update_data['description'] = description
                        
                        updated_product = self.product_service.update_product(
                            existing_product.product_id, 
                            **update_data
                        )
                        print(f"Product updated: {updated_product.name}, ${updated_product.price:.2f}")
                    except ValueError as e:
                        print(f"Error updating product: {str(e)}")
                    
                    continue
                
                # Enter product details
                try:
                    name = input("Product name: ")
                    if not name:
                        print("Product name is required")
                        continue
                    
                    price_str = input("Price ($): ")
                    try:
                        price = float(price_str)
                    except ValueError:
                        print("Invalid price format")
                        continue
                    
                    category_id = None
                    if args.show_categories:
                        self._list_categories()
                        cat_input = input("Category ID (optional): ")
                        if cat_input:
                            try:
                                category_id = int(cat_input)
                            except ValueError:
                                print("Invalid category ID. No category will be assigned.")
                    
                    description = input("Description (optional): ")
                    
                    # Create the product
                    product = self.product_service.create_product(
                        barcode=barcode,
                        name=name,
                        price=price,
                        category_id=category_id,
                        description=description
                    )
                    
                    print(f"Product added: {product.name} (ID: {product.product_id})")
                    print(f"Barcode: {product.barcode}, Price: ${product.price:.2f}")
                    
                except ValueError as e:
                    print(f"Error: {str(e)}")
                except KeyboardInterrupt:
                    print("\nProduct addition cancelled")
        
        except KeyboardInterrupt:
            print("\n\nScan mode exited.")
        
        return True
    
    def _list_categories(self):
        """Display a list of available categories"""
        categories = self.session.query(Category).all()
        
        if not categories:
            print("No categories found")
            return
        
        print("\nAvailable Categories:")
        print("=" * 40)
        print(f"{'ID':<5} {'Name'}")
        print("-" * 40)
        
        for category in categories:
            print(f"{category.category_id:<5} {category.name}")
        
        print("=" * 40)

    def scan_check_in(self, args):
        """Interactive mode to scan barcodes and check in products"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        # Verify warehouse exists
        if not args.warehouse:
            print("Error: Warehouse ID is required")
            return False
        
        from ..models import Warehouse
        warehouse = self.session.query(Warehouse).filter(Warehouse.warehouse_id == args.warehouse).first()
        if not warehouse:
            print(f"Error: Warehouse with ID {args.warehouse} not found")
            return False
        
        print(f"\n=== Check-In Scan Mode (Warehouse: {warehouse.name}) ===")
        print("Scan product barcodes and enter quantities. Press Ctrl+C to exit.\n")
        
        from ..services import InventoryService
        inventory_service = InventoryService(self.session)
        
        scanned_count = 0
        
        try:
            while True:
                # Step 1: Scan barcode
                barcode = read_barcode_from_scanner("Scan barcode (or press Enter to finish): ")
                
                if not barcode:
                    break
                
                # Validate barcode format
                valid, error = validate_barcode(barcode)
                if not valid:
                    print(f"Invalid barcode: {error}")
                    continue
                
                # Check if product exists
                product = self.product_service.get_product_by_barcode(barcode)
                if not product:
                    print(f"Product with barcode '{barcode}' not found")
                    if args.add_missing:
                        add_new = input("Do you want to add this as a new product? (y/n): ").lower()
                        if add_new == 'y':
                            try:
                                name = input("Product name: ")
                                if not name:
                                    print("Product name is required")
                                    continue
                                
                                price_str = input("Price ($): ")
                                try:
                                    price = float(price_str)
                                except ValueError:
                                    print("Invalid price format")
                                    continue
                                
                                product = self.product_service.create_product(
                                    barcode=barcode,
                                    name=name,
                                    price=price
                                )
                                
                                print(f"Product added: {product.name} (ID: {product.product_id})")
                            except ValueError as e:
                                print(f"Error adding product: {str(e)}")
                                continue
                        else:
                            continue
                    else:
                        continue
                
                # Display product info
                print(f"Product: {product.name}, Price: ${product.price:.2f}")
                
                # Step 2: Enter quantity
                try:
                    quantity_str = input("Quantity: ")
                    quantity = float(quantity_str)
                    
                    if quantity <= 0:
                        print("Quantity must be greater than zero")
                        continue
                    
                    notes = input("Notes (optional): ")
                    
                    # Step 3: Check in the product
                    inventory_item, transaction = inventory_service.check_in(
                        barcode=barcode,
                        warehouse_id=args.warehouse,
                        quantity=quantity,
                        user_id=current_user.user_id,
                        notes=notes
                    )
                    
                    print(f"Successfully checked in {quantity} units of {product.name}")
                    print(f"Current stock in warehouse: {inventory_item.quantity}")
                    scanned_count += 1
                    
                except ValueError as e:
                    print(f"Error: {str(e)}")
                except KeyboardInterrupt:
                    print("\nCheck-in cancelled")
        
        except KeyboardInterrupt:
            pass
        
        print(f"\nCheck-in complete. Processed {scanned_count} items.")
        return True