from ..services import ProductService

class ProductCommands:
    """Commands for product management"""
    
    def __init__(self, session, auth_commands):
        self.product_service = ProductService(session)
        self.auth_commands = auth_commands
    
    def list_products(self, args):
        """List all products"""
        products = self.product_service.get_all_products()
        if not products:
            print("No products found")
            return True
        
        print("\nProducts:")
        print("=" * 80)
        print(f"{'ID':<5} {'Barcode':<15} {'Name':<30} {'Category':<10} {'Price':<10}")
        print("-" * 80)
        
        for product in products:
            category = product.category.name if product.category else 'N/A'
            print(f"{product.product_id:<5} {product.barcode:<15} {product.name:<30} {category:<10} ${product.price:.2f}")
        
        print("=" * 80)
        return True
    
    def add_product(self, args):
        """Add a new product"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        # Check if user has sufficient permissions
        if current_user.role not in ['admin', 'manager']:
            print("Error: Insufficient permissions")
            return False
        
        try:
            product = self.product_service.create_product(
                barcode=args.barcode,
                name=args.name,
                price=args.price,
                category_id=args.category,
                description=args.description
            )
            print(f"Product '{product.name}' added successfully with ID {product.product_id}")
            return True
        except ValueError as e:
            print(f"Error: {str(e)}")
            return False
    
    def update_product(self, args):
        """Update a product"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        # Check if user has sufficient permissions
        if current_user.role not in ['admin', 'manager']:
            print("Error: Insufficient permissions")
            return False
        
        # Collect update fields
        update_fields = {}
        if args.name is not None:
            update_fields['name'] = args.name
        if args.barcode is not None:
            update_fields['barcode'] = args.barcode
        if args.price is not None:
            update_fields['price'] = args.price
        if args.category is not None:
            update_fields['category_id'] = args.category
        if args.description is not None:
            update_fields['description'] = args.description
        
        if not update_fields:
            print("Error: No update fields provided")
            return False
        
        try:
            product = self.product_service.update_product(args.id, **update_fields)
            if product:
                print(f"Product {product.product_id} updated successfully")
                return True
            else:
                print(f"Error: Product with ID {args.id} not found")
                return False
        except ValueError as e:
            print(f"Error: {str(e)}")
            return False
    
    def delete_product(self, args):
        """Delete a product"""
        # Check if user is logged in with admin permissions
        current_user = self.auth_commands.get_current_user()
        if not current_user or current_user.role != 'admin':
            print("Error: Admin privileges required")
            return False
        
        result = self.product_service.delete_product(args.id)
        if result:
            print(f"Product with ID {args.id} deleted successfully")
            return True
        else:
            print(f"Error: Product with ID {args.id} not found")
            return False
    
    def search_product(self, args):
        """Search for products"""
        # By barcode (exact match)
        if args.barcode:
            products = self.product_service.search_products(barcode=args.barcode)
        # By name (partial match)
        elif args.name:
            products = self.product_service.search_products(name=args.name)
        # By category
        elif args.category:
            products = self.product_service.search_products(category_id=args.category)
        else:
            print("Error: No search criteria provided")
            return False
        
        if not products:
            print("No matching products found")
            return True
        
        print("\nSearch Results:")
        print("=" * 80)
        print(f"{'ID':<5} {'Barcode':<15} {'Name':<30} {'Category':<10} {'Price':<10}")
        print("-" * 80)
        
        for product in products:
            category = product.category.name if product.category else 'N/A'
            print(f"{product.product_id:<5} {product.barcode:<15} {product.name:<30} {category:<10} ${product.price:.2f}")
        
        print("=" * 80)
        return True