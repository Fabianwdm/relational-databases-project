#!/usr/bin/env python3
# menu_interface.py

import os
import sys
from inventory.models import Base, get_engine, get_session
from inventory.cli.auth_commands import AuthCommands
from inventory.cli.product_commands import ProductCommands
from inventory.cli.inventory_commands import InventoryCommands
from inventory.cli.report_commands import ReportCommands
from inventory.cli.scan_commands import ScanCommands
from inventory.models import User, Warehouse, Category, Product, Inventory

class MenuInterface:
    """Interactive menu-based interface for the Barcode Inventory System"""
    
    def __init__(self):
        # Default database path
        self.db_path = os.path.expanduser("~/inventory.db")
        
        # Initialize database and get session
        self.session = self.init_db()
        
        # Initialize command handlers
        self.auth_commands = AuthCommands(self.session)
        self.product_commands = ProductCommands(self.session, self.auth_commands)
        self.inventory_commands = InventoryCommands(self.session, self.auth_commands)
        self.report_commands = ReportCommands(self.session, self.auth_commands)
        self.scan_commands = ScanCommands(self.session, self.auth_commands)
        
        # Current user
        self.current_user = None
    
    def init_db(self):
        """Initialize the database"""
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Create database engine and tables
        engine = get_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(engine)
        
        # Create session
        session = get_session(engine)
        
        # Check if admin user exists, create one if not
        admins = session.query(User).filter(User.role == 'admin').first()
        
        if not admins:
            # Create admin user
            from inventory.services import UserService
            user_service = UserService(session)
            try:
                admin = user_service.create_user(
                    username="admin",
                    password="admin",  # Default password, should be changed immediately
                    email="admin@inventory.local",
                    role="admin"
                )
                print("Created default admin user.")
                print("Username: admin")
                print("Password: admin")
                print("IMPORTANT: Please change the default password immediately!")
            except ValueError:
                # Admin user already exists
                pass
        
        return session
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the application header"""
        self.clear_screen()
        print("=" * 60)
        print("               BARCODE INVENTORY SYSTEM")
        print("=" * 60)
        if self.current_user:
            print(f"Logged in as: {self.current_user.username} ({self.current_user.role})")
        else:
            print("Not logged in")
        print("-" * 60)
    
    def input_with_default(self, prompt, default=None):
        """Get user input with an optional default value"""
        if default:
            result = input(f"{prompt} [{default}]: ")
            return result if result else default
        else:
            return input(f"{prompt}: ")
    
    def pause(self):
        """Pause and wait for user input before continuing"""
        input("\nPress Enter to continue...")
    
    def login_menu(self):
        """Display login menu"""
        while True:
            self.print_header()
            print("\nLOGIN MENU")
            print("1. Login")
            print("2. Exit")
            
            choice = input("\nEnter your choice (1-2): ")
            
            if choice == '1':
                username = input("Username: ")
                password = input("Password: ")
                
                # Create args object to pass to login command
                class Args:
                    pass
                
                args = Args()
                args.username = username
                args.password = password
                
                if self.auth_commands.login(args):
                    self.current_user = self.auth_commands.get_current_user()
                    self.main_menu()
                    return  # Return to login menu after logging out
                else:
                    self.pause()
            
            elif choice == '2':
                print("\nGoodbye!")
                sys.exit(0)
            
            else:
                print("\nInvalid choice. Please try again.")
                self.pause()
    
    def main_menu(self):
        """Display main menu"""
        while True:
            self.print_header()
            print("\nMAIN MENU")
            print("1. Products")
            print("2. Inventory")
            print("3. Reports")
            print("4. Scan Mode")
            print("5. User Management")
            print("6. Logout")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == '1':
                self.product_menu()
            elif choice == '2':
                self.inventory_menu()
            elif choice == '3':
                self.report_menu()
            elif choice == '4':
                self.scan_menu()
            elif choice == '5':
                self.user_menu()
            elif choice == '6':
                # Logout
                class Args:
                    pass
                
                args = Args()
                if self.auth_commands.logout(args):
                    self.current_user = None
                    return  # Return to login menu
            elif choice == '7':
                # Exit
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("\nInvalid choice. Please try again.")
                self.pause()
    
    def product_menu(self):
        """Display product management menu"""
        while True:
            self.print_header()
            print("\nPRODUCT MENU")
            print("1. List All Products")
            print("2. Add New Product")
            print("3. Update Product")
            print("4. Delete Product")
            print("5. Search Products")
            print("6. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-6): ")
            
            class Args:
                pass
            
            args = Args()
            
            if choice == '1':
                self.product_commands.list_products(args)
                self.pause()
            
            elif choice == '2':
                args.barcode = input("Barcode: ")
                args.name = input("Name: ")
                
                price_str = input("Price: $")
                try:
                    args.price = float(price_str)
                except ValueError:
                    print("Invalid price format")
                    self.pause()
                    continue
                
                # Show categories
                categories = self.session.query(Category).all()
                if categories:
                    print("\nAvailable Categories:")
                    for cat in categories:
                        print(f"{cat.category_id}: {cat.name}")
                    
                    cat_id = input("\nCategory ID (optional): ")
                    args.category = int(cat_id) if cat_id.isdigit() else None
                else:
                    args.category = None
                
                args.description = input("Description (optional): ")
                
                self.product_commands.add_product(args)
                self.pause()
            
            elif choice == '3':
                id_str = input("Product ID to update: ")
                if not id_str.isdigit():
                    print("Invalid product ID")
                    self.pause()
                    continue
                
                args.id = int(id_str)
                
                # Show current product
                product = self.session.query(Product).get(args.id)
                if not product:
                    print(f"Product with ID {args.id} not found")
                    self.pause()
                    continue
                
                print(f"\nCurrent Product: {product.name} (Barcode: {product.barcode})")
                print("Leave blank to keep current value")
                
                args.barcode = input("New barcode (optional): ")
                args.name = input("New name (optional): ")
                
                price_str = input("New price (optional): $")
                args.price = float(price_str) if price_str else None
                
                cat_id = input("New category ID (optional): ")
                args.category = int(cat_id) if cat_id.isdigit() else None
                
                args.description = input("New description (optional): ")
                
                self.product_commands.update_product(args)
                self.pause()
            
            elif choice == '4':
                id_str = input("Product ID to delete: ")
                if not id_str.isdigit():
                    print("Invalid product ID")
                    self.pause()
                    continue
                
                args.id = int(id_str)
                
                confirm = input(f"Are you sure you want to delete product {args.id}? (y/n): ")
                if confirm.lower() == 'y':
                    self.product_commands.delete_product(args)
                
                self.pause()
            
            elif choice == '5':
                print("\nSearch by:")
                print("1. Barcode")
                print("2. Name")
                print("3. Category")
                
                search_choice = input("\nEnter your choice (1-3): ")
                
                if search_choice == '1':
                    args.barcode = input("Barcode to search: ")
                    args.name = None
                    args.category = None
                elif search_choice == '2':
                    args.name = input("Name to search: ")
                    args.barcode = None
                    args.category = None
                elif search_choice == '3':
                    cat_id = input("Category ID: ")
                    args.category = int(cat_id) if cat_id.isdigit() else None
                    args.barcode = None
                    args.name = None
                else:
                    print("Invalid choice")
                    self.pause()
                    continue
                
                self.product_commands.search_product(args)
                self.pause()
            
            elif choice == '6':
                return
            
            else:
                print("\nInvalid choice. Please try again.")
                self.pause()
    
    def inventory_menu(self):
        """Display inventory management menu"""
        while True:
            self.print_header()
            print("\nINVENTORY MENU")
            print("1. Check In Products")
            print("2. Check Out Products")
            print("3. Transfer Products")
            print("4. Set Minimum Stock Levels")  # Added this option
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-5): ")  # Updated range
            
            class Args:
                pass
            
            args = Args()
            
            if choice in ['1', '2']:
                args.barcode = input("Product barcode: ")
                
                # Show warehouses
                warehouses = self.session.query(Warehouse).all()
                if warehouses:
                    print("\nAvailable Warehouses:")
                    for wh in warehouses:
                        print(f"{wh.warehouse_id}: {wh.name} ({wh.location})")
                    
                    wh_id = input("\nWarehouse ID: ")
                    if not wh_id.isdigit():
                        print("Invalid warehouse ID")
                        self.pause()
                        continue
                    
                    args.warehouse = int(wh_id)
                else:
                    print("No warehouses available. Please create a warehouse first.")
                    self.pause()
                    continue
                
                qty_str = input("Quantity: ")
                try:
                    args.quantity = float(qty_str)
                except ValueError:
                    print("Invalid quantity format")
                    self.pause()
                    continue
                
                args.notes = input("Notes (optional): ")
                
                if choice == '1':
                    self.inventory_commands.check_in(args)
                else:  # choice == '2'
                    self.inventory_commands.check_out(args)
                
                self.pause()
            
            elif choice == '3':
                args.barcode = input("Product barcode: ")
                
                # Show warehouses
                warehouses = self.session.query(Warehouse).all()
                if warehouses:
                    print("\nAvailable Warehouses:")
                    for wh in warehouses:
                        print(f"{wh.warehouse_id}: {wh.name} ({wh.location})")
                    
                    from_wh_id = input("\nSource Warehouse ID: ")
                    if not from_wh_id.isdigit():
                        print("Invalid warehouse ID")
                        self.pause()
                        continue
                    
                    args.from_warehouse = int(from_wh_id)
                    
                    to_wh_id = input("Destination Warehouse ID: ")
                    if not to_wh_id.isdigit():
                        print("Invalid warehouse ID")
                        self.pause()
                        continue
                    
                    args.to_warehouse = int(to_wh_id)
                else:
                    print("No warehouses available. Please create a warehouse first.")
                    self.pause()
                    continue
                
                qty_str = input("Quantity: ")
                try:
                    args.quantity = float(qty_str)
                except ValueError:
                    print("Invalid quantity format")
                    self.pause()
                    continue
                
                args.notes = input("Notes (optional): ")
                
                self.inventory_commands.transfer(args)
                self.pause()
            
            elif choice == '4':
                # New option to set minimum stock levels
                self.set_minimum_stock_levels()
            
            elif choice == '5':  # Updated number
                return
            
            else:
                print("\nInvalid choice. Please try again.")
                self.pause()
    
    def set_minimum_stock_levels(self):
        """Set minimum stock levels for products in warehouses"""
        self.print_header()
        print("\nSET MINIMUM STOCK LEVELS")
        print("This will set the minimum stock level for a product in a specific warehouse.")
        print("When stock falls below this level, it will appear in low stock reports.")
        
        # Option to search by barcode or product ID
        print("\nSearch product by:")
        print("1. Barcode")
        print("2. Product ID")
        
        search_choice = input("\nEnter your choice (1-2): ")
        
        from inventory.models import Product, Inventory
        from sqlalchemy import and_
        
        product = None
        
        if search_choice == '1':
            barcode = input("Enter product barcode: ")
            product = self.session.query(Product).filter(Product.barcode == barcode).first()
        elif search_choice == '2':
            product_id = input("Enter product ID: ")
            if product_id.isdigit():
                product = self.session.query(Product).get(int(product_id))
        else:
            print("Invalid choice")
            self.pause()
            return
        
        if not product:
            print("Product not found")
            self.pause()
            return
        
        print(f"\nSelected product: {product.name} (ID: {product.product_id}, Barcode: {product.barcode})")
        
        # Show warehouses where this product exists in inventory
        inventory_items = self.session.query(Inventory, Warehouse).join(Warehouse) \
                             .filter(Inventory.product_id == product.product_id).all()
        
        if not inventory_items:
            print("This product is not currently in any warehouse inventory.")
            add_new = input("Would you like to add it to a warehouse? (y/n): ")
            if add_new.lower() != 'y':
                self.pause()
                return
            
            # Show all warehouses
            warehouses = self.session.query(Warehouse).all()
            if not warehouses:
                print("No warehouses available. Please create a warehouse first.")
                self.pause()
                return
            
            print("\nAvailable Warehouses:")
            for wh in warehouses:
                print(f"{wh.warehouse_id}: {wh.name} ({wh.location})")
            
            warehouse_id = input("\nSelect warehouse ID: ")
            if not warehouse_id.isdigit():
                print("Invalid warehouse ID")
                self.pause()
                return
            
            warehouse_id = int(warehouse_id)
            warehouse = self.session.query(Warehouse).get(warehouse_id)
            if not warehouse:
                print("Warehouse not found")
                self.pause()
                return
            
            # Create new inventory entry with zero quantity
            new_inventory = Inventory(
                product_id=product.product_id,
                warehouse_id=warehouse_id,
                quantity=0
            )
            
            min_stock_str = input("Enter minimum stock level: ")
            try:
                min_stock = float(min_stock_str)
                if min_stock < 0:
                    raise ValueError("Minimum stock cannot be negative")
                
                new_inventory.minimum_stock = min_stock
                self.session.add(new_inventory)
                self.session.commit()
                
                print(f"Added {product.name} to {warehouse.name} with minimum stock level of {min_stock}")
                self.pause()
                return
            except ValueError as e:
                print(f"Invalid minimum stock value: {str(e)}")
                self.pause()
                return
        
        # Show existing inventory items
        print("\nCurrent inventory locations:")
        print(f"{'#':<3} {'Warehouse':<20} {'Current Qty':<12} {'Min Stock':<12}")
        print("-" * 60)
        
        for i, (inv, wh) in enumerate(inventory_items, 1):
            print(f"{i:<3} {wh.name:<20} {inv.quantity:<12.2f} {inv.minimum_stock or 'Not set':<12}")
        
        # Select which inventory to update
        sel = input("\nSelect inventory number to update (or 0 to cancel): ")
        if not sel.isdigit() or int(sel) < 1 or int(sel) > len(inventory_items):
            if sel == '0':
                return
            print("Invalid selection")
            self.pause()
            return
        
        selected_inv, selected_wh = inventory_items[int(sel) - 1]
        
        # Set minimum stock level
        min_stock_str = input(f"Enter new minimum stock level for {product.name} in {selected_wh.name}: ")
        try:
            min_stock = float(min_stock_str)
            if min_stock < 0:
                raise ValueError("Minimum stock cannot be negative")
            
            selected_inv.minimum_stock = min_stock
            self.session.commit()
            
            print(f"Minimum stock level updated to {min_stock}")
            
            # Check if current stock is below minimum
            if selected_inv.quantity < min_stock:
                print(f"\nWARNING: Current stock ({selected_inv.quantity}) is below minimum stock level ({min_stock})!")
        except ValueError as e:
            print(f"Invalid minimum stock value: {str(e)}")
        
        self.pause()
    
    def report_menu(self):
        """Display report generation menu"""
        while True:
            self.print_header()
            print("\nREPORT MENU")
            print("1. Inventory Report")
            print("2. Transaction Report")
            print("3. Low Stock Report")
            print("4. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-4): ")
            
            class Args:
                pass
            
            args = Args()
            
            if choice == '1':
                # Show warehouses
                warehouses = self.session.query(Warehouse).all()
                if warehouses:
                    print("\nAvailable Warehouses:")
                    print("0: All Warehouses")
                    for wh in warehouses:
                        print(f"{wh.warehouse_id}: {wh.name} ({wh.location})")
                    
                    wh_id = input("\nWarehouse ID (or 0 for all): ")
                    args.warehouse = int(wh_id) if wh_id.isdigit() and int(wh_id) > 0 else None
                else:
                    args.warehouse = None
                
                self.report_commands.inventory_report(args)
                self.pause()
            
            elif choice == '2':
                args.date_from = input("Start date (YYYY-MM-DD) or leave blank for last 30 days: ")
                args.date_to = input("End date (YYYY-MM-DD) or leave blank for today: ")
                
                # Show warehouses
                warehouses = self.session.query(Warehouse).all()
                if warehouses:
                    print("\nAvailable Warehouses:")
                    print("0: All Warehouses")
                    for wh in warehouses:
                        print(f"{wh.warehouse_id}: {wh.name} ({wh.location})")
                    
                    wh_id = input("\nWarehouse ID (or 0 for all): ")
                    args.warehouse = int(wh_id) if wh_id.isdigit() and int(wh_id) > 0 else None
                else:
                    args.warehouse = None
                
                product_id = input("Product ID (optional): ")
                args.product = int(product_id) if product_id.isdigit() else None
                
                self.report_commands.transaction_report(args)
                self.pause()
            
            elif choice == '3':
                threshold = input("Stock threshold (optional): ")
                args.threshold = float(threshold) if threshold else None
                
                self.report_commands.low_stock_report(args)
                self.pause()
            
            elif choice == '4':
                return
            
            else:
                print("\nInvalid choice. Please try again.")
                self.pause()
    
    def scan_menu(self):
        """Display barcode scanning menu"""
        while True:
            self.print_header()
            print("\nSCAN MENU")
            print("1. Scan and Add Products")
            print("2. Scan and Check In Products")
            print("3. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-3): ")
            
            class Args:
                pass
            
            args = Args()
            
            if choice == '1':
                args.show_categories = True
                self.scan_commands.scan_and_add(args)
                self.pause()
            
            elif choice == '2':
                # Show warehouses
                warehouses = self.session.query(Warehouse).all()
                if warehouses:
                    print("\nAvailable Warehouses:")
                    for wh in warehouses:
                        print(f"{wh.warehouse_id}: {wh.name} ({wh.location})")
                    
                    wh_id = input("\nWarehouse ID: ")
                    if not wh_id.isdigit():
                        print("Invalid warehouse ID")
                        self.pause()
                        continue
                    
                    args.warehouse = int(wh_id)
                else:
                    print("No warehouses available. Please create a warehouse first.")
                    self.pause()
                    continue
                
                args.add_missing = True
                self.scan_commands.scan_check_in(args)
                self.pause()
            
            elif choice == '3':
                return
            
            else:
                print("\nInvalid choice. Please try again.")
                self.pause()
    
    def user_menu(self):
        """Display user management menu"""
        while True:
            self.print_header()
            print("\nUSER MENU")
            print("1. List Users")
            print("2. Add User")
            print("3. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-3): ")
            
            class Args:
                pass
            
            args = Args()
            
            if choice == '1':
                self.auth_commands.list_users(args)
                self.pause()
            
            elif choice == '2':
                args.username = input("Username: ")
                args.password = input("Password: ")
                args.email = input("Email (optional): ")
                
                print("\nAvailable roles:")
                print("1. Admin")
                print("2. Manager")
                print("3. Staff")
                
                role_choice = input("\nRole (1-3): ")
                
                if role_choice == '1':
                    args.role = 'admin'
                elif role_choice == '2':
                    args.role = 'manager'
                else:
                    args.role = 'staff'
                
                self.auth_commands.create_user(args)
                self.pause()
            
            elif choice == '3':
                return
            
            else:
                print("\nInvalid choice. Please try again.")
                self.pause()
    
    def run(self):
        """Run the menu interface"""
        try:
            self.login_menu()
        except KeyboardInterrupt:
            print("\n\nExiting the application...")
            sys.exit(0)
        finally:
            self.session.close()

if __name__ == '__main__':
    menu = MenuInterface()
    menu.run()
