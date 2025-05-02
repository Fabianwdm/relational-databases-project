#!/usr/bin/env python3
# generate_sample_data.py

import os
import random
from datetime import datetime, timedelta
import argparse
from inventory.models import Base, get_engine, get_session
from inventory.models import Category, Product, Warehouse, User, Supplier, ProductSupplier, Inventory, Transaction
from inventory.services import UserService

def generate_users(session, count=5):
    """Generate sample users"""
    print(f"Generating {count} users...")
    
    user_service = UserService(session)
    
    # Create admin user if it doesn't exist
    try:
        admin = user_service.create_user(
            username="admin",
            password="admin",
            email="admin@inventory.local",
            role="admin"
        )
        print("Created admin user")
    except ValueError:
        print("Admin user already exists")
    
    # Create manager
    try:
        manager = user_service.create_user(
            username="manager",
            password="manager",
            email="manager@inventory.local",
            role="manager"
        )
        print("Created manager user")
    except ValueError:
        print("Manager user already exists")
    
    # Create staff users
    staff_created = 0
    for i in range(count):
        try:
            user = user_service.create_user(
                username=f"staff{i+1}",
                password=f"staff{i+1}",
                email=f"staff{i+1}@inventory.local",
                role="staff"
            )
            staff_created += 1
        except ValueError:
            pass
    
    print(f"Created {staff_created} staff users")
    return staff_created + 2  # Including admin and manager

def generate_categories(session, count=10):
    """Generate sample categories"""
    print(f"Generating {count} categories...")
    
    categories = []
    category_names = [
        "Electronics", "Clothing", "Home Goods", "Books", "Toys",
        "Sports", "Automotive", "Health", "Beauty", "Food",
        "Office Supplies", "Tools", "Garden", "Pet Supplies", "Music"
    ]
    
    # Shuffle and select the required number
    random.shuffle(category_names)
    selected_categories = category_names[:count]
    
    for name in selected_categories:
        category = Category(
            name=name,
            description=f"Products in the {name.lower()} category"
        )
        session.add(category)
        categories.append(category)
    
    session.commit()
    print(f"Created {len(categories)} categories")
    return categories

def generate_warehouses(session, count=5):
    """Generate sample warehouses"""
    print(f"Generating {count} warehouses...")
    
    warehouses = []
    warehouse_locations = [
        "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt",
        "Stuttgart", "Düsseldorf", "Leipzig", "Dortmund", "Essen"
    ]
    
    # Shuffle and select the required number
    random.shuffle(warehouse_locations)
    selected_locations = warehouse_locations[:count]
    
    for i, location in enumerate(selected_locations):
        warehouse = Warehouse(
            name=f"{location} Warehouse",
            location=location,
            capacity=random.randint(5000, 20000),
            status=random.choice(['active', 'active', 'active', 'maintenance'])
        )
        session.add(warehouse)
        warehouses.append(warehouse)
    
    session.commit()
    print(f"Created {len(warehouses)} warehouses")
    return warehouses

def generate_suppliers(session, count=10):
    """Generate sample suppliers"""
    print(f"Generating {count} suppliers...")
    
    suppliers = []
    supplier_names = [
        "Acme Corp", "Widget Co", "Best Supply", "Quality Goods",
        "Fast Delivery", "Global Imports", "Local Products", "Top Tier",
        "ValueMax", "Prime Source", "Mega Distributors", "Supply Chain Pro",
        "Rapid Logistics", "Reliable Partners", "Industry Leaders"
    ]
    
    # Shuffle and select the required number
    random.shuffle(supplier_names)
    selected_suppliers = supplier_names[:count]
    
    for name in selected_suppliers:
        supplier = Supplier(
            name=name,
            contact_person=f"{random.choice(['John', 'Jane', 'Sam', 'Alex'])} {random.choice(['Smith', 'Doe', 'Johnson', 'Brown'])}",
            email=f"contact@{name.lower().replace(' ', '')}.com",
            phone=f"+49 {random.randint(100, 999)} {random.randint(1000000, 9999999)}",
            address=f"{random.randint(1, 100)} {random.choice(['Main', 'Market', 'Industrial', 'Commerce'])} St, {random.choice(['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt'])}"
        )
        session.add(supplier)
        suppliers.append(supplier)
    
    session.commit()
    print(f"Created {len(suppliers)} suppliers")
    return suppliers

def generate_products(session, categories, suppliers, count=100):
    """Generate sample products"""
    print(f"Generating {count} products...")
    
    products = []
    product_prefixes = ["Super", "Ultra", "Mega", "Pro", "Max", "Deluxe", "Premium", "Basic", "Standard", "Elite"]
    product_types = ["Widget", "Gadget", "Tool", "Device", "System", "Kit", "Set", "Pack", "Box", "Solution"]
    
    for i in range(count):
        # Generate a unique barcode
        barcode = f"BCD-{random.randint(100000, 999999)}"
        
        # Select a random name
        name = f"{random.choice(product_prefixes)} {random.choice(product_types)} {random.randint(100, 999)}"
        
        # Select a random category
        category = random.choice(categories)
        
        product = Product(
            barcode=barcode,
            name=name,
            description=f"This is a {name.lower()} in the {category.name} category",
            category_id=category.category_id,
            price=round(random.uniform(9.99, 199.99), 2)
        )
        session.add(product)
        session.flush()  # Flush to get product ID
        products.append(product)
        
        # Create product-supplier relationships (1-3 suppliers per product)
        supplier_count = random.randint(1, 3)
        product_suppliers = random.sample(suppliers, supplier_count)
        
        for supplier in product_suppliers:
            product_supplier = ProductSupplier(
                product_id=product.product_id,
                supplier_id=supplier.supplier_id,
                lead_time=random.randint(1, 14),  # 1-14 days
                price=round(product.price * random.uniform(0.6, 0.8), 2)  # 60-80% of retail price
            )
            session.add(product_supplier)
    
    session.commit()
    print(f"Created {len(products)} products with supplier relationships")
    return products

def generate_inventory(session, products, warehouses):
    """Generate sample inventory data"""
    print("Generating inventory data...")
    
    inventory_items = []
    
    # Distribute products across warehouses (not all products in all warehouses)
    for product in products:
        # Choose 1-3 random warehouses for this product
        warehouse_count = random.randint(1, min(3, len(warehouses)))
        product_warehouses = random.sample(warehouses, warehouse_count)
        
        for warehouse in product_warehouses:
            # Generate random inventory quantity
            quantity = random.randint(0, 100)
            min_stock = random.randint(5, 20)
            
            inventory_item = Inventory(
                product_id=product.product_id,
                warehouse_id=warehouse.warehouse_id,
                quantity=quantity,
                minimum_stock=min_stock,
                last_checked=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            session.add(inventory_item)
            inventory_items.append(inventory_item)
    
    session.commit()
    print(f"Created {len(inventory_items)} inventory records")
    return inventory_items

def generate_transactions(session, inventory_items, users, count=1000):
    """Generate sample transaction history"""
    print(f"Generating {count} transactions...")
    
    transactions = []
    
    # Get list of valid user IDs
    user_ids = [user.user_id for user in users]
    
    # Generate random transactions
    for _ in range(count):
        # Pick a random inventory item
        inv_item = random.choice(inventory_items)
        
        # Determine transaction type
        transaction_type = random.choice(['check-in', 'check-out'])
        
        # Generate random quantity
        quantity = random.randint(1, 20)
        
        # Generate random timestamp within last 90 days
        timestamp = datetime.utcnow() - timedelta(days=random.randint(0, 90))
        
        transaction = Transaction(
            product_id=inv_item.product_id,
            warehouse_id=inv_item.warehouse_id,
            user_id=random.choice(user_ids),
            quantity=quantity,
            transaction_type=transaction_type,
            timestamp=timestamp,
            notes="Automatically generated transaction"
        )
        session.add(transaction)
        transactions.append(transaction)
    
    session.commit()
    print(f"Created {len(transactions)} transactions")
    return transactions

def main():
    parser = argparse.ArgumentParser(description='Generate sample data for Barcode Inventory System')
    parser.add_argument('--db-path', default=os.path.expanduser("~/inventory.db"), help='Database path')
    args = parser.parse_args()
    
    # Create engine and session
    engine = get_engine(f"sqlite:///{args.db_path}")
    Base.metadata.create_all(engine)
    session = get_session(engine)
    
    try:
        # Generate data
        users = generate_users(session)
        categories = generate_categories(session)
        warehouses = generate_warehouses(session)
        suppliers = generate_suppliers(session)
        products = generate_products(session, categories, suppliers)
        inventory_items = generate_inventory(session, products, warehouses)
        transactions = generate_transactions(session, inventory_items, session.query(User).all())
        
        print("\nSample data generation complete!")
        print(f"Database: {args.db_path}")
        print("\nSummary:")
        print(f"- Users: {users}")
        print(f"- Categories: {len(categories)}")
        print(f"- Warehouses: {len(warehouses)}")
        print(f"- Suppliers: {len(suppliers)}")
        print(f"- Products: {len(products)}")
        print(f"- Inventory Items: {len(inventory_items)}")
        print(f"- Transactions: {len(transactions)}")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    main()