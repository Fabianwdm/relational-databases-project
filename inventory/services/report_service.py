from datetime import datetime, timedelta
from ..repositories import InventoryRepository, TransactionRepository, ProductRepository
from tabulate import tabulate

class ReportService:
    
    def __init__(self, session):
        self.inventory_repo = InventoryRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.product_repo = ProductRepository(session)
        self.session = session
    
    def generate_inventory_report(self, warehouse_id=None):
        report_data = []
        
        if warehouse_id:
            # Get inventory for specific warehouse
            inventory_items = self.inventory_repo.get_warehouse_inventory(warehouse_id)
            
            for inv, product in inventory_items:
                report_data.append({
                    'Product ID': product.product_id,
                    'Barcode': product.barcode,
                    'Name': product.name,
                    'Quantity': inv.quantity,
                    'Min Stock': inv.minimum_stock,
                    'Last Checked': inv.last_checked.strftime('%Y-%m-%d %H:%M:%S')
                })
                
            report_title = f"Inventory Report for Warehouse #{warehouse_id}"
        else:
            # Get inventory across all warehouses
            inventory_items = self.inventory_repo.get_all()
            warehouses = {}
            
            for inv in inventory_items:
                product = self.product_repo.get_by_id(inv.product_id)
                
                report_data.append({
                    'Product ID': product.product_id,
                    'Barcode': product.barcode,
                    'Name': product.name,
                    'Warehouse ID': inv.warehouse_id,
                    'Quantity': inv.quantity,
                    'Min Stock': inv.minimum_stock,
                    'Last Checked': inv.last_checked.strftime('%Y-%m-%d %H:%M:%S')
                })
                
            report_title = "Inventory Report for All Warehouses"
        
        # Format as text table
        if report_data:
            table = tabulate(report_data, headers="keys", tablefmt="grid")
            return report_title, table
        else:
            return report_title, "No inventory data found."
    
    def generate_transaction_report(self, start_date=None, end_date=None, product_id=None, warehouse_id=None):
        report_data = []
        
        # Set default date range to last 30 days if not specified
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
            
        # Get transactions
        if start_date and end_date:
            transactions = self.transaction_repo.get_transactions_by_date_range(start_date, end_date)
            report_title = f"Transaction Report from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            
            for trans, product, warehouse, user in transactions:
                if (product_id is None or trans.product_id == product_id) and \
                   (warehouse_id is None or trans.warehouse_id == warehouse_id):
                    report_data.append({
                        'Transaction ID': trans.transaction_id,
                        'Date': trans.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'Type': trans.transaction_type,
                        'Product': product.name,
                        'Barcode': product.barcode,
                        'Warehouse': warehouse.name,
                        'Quantity': trans.quantity,
                        'User': user.username,
                        'Notes': trans.notes or ''
                    })
        
        # Format as text table
        if report_data:
            table = tabulate(report_data, headers="keys", tablefmt="grid")
            return report_title, table
        else:
            return report_title, "No transaction data found for the specified criteria."
    
    def generate_low_stock_report(self, threshold=None):
        low_stock_items = self.inventory_repo.get_low_stock_items(threshold)
        report_data = []
        
        for inv, product, warehouse in low_stock_items:
            report_data.append({
                'Product ID': product.product_id,
                'Barcode': product.barcode,
                'Name': product.name,
                'Warehouse': warehouse.name,
                'Current Quantity': inv.quantity,
                'Minimum Stock': inv.minimum_stock
            })
        
        report_title = "Low Stock Report"
        if threshold is not None:
            report_title += f" (Threshold: {threshold})"
        
        # Format as text table
        if report_data:
            table = tabulate(report_data, headers="keys", tablefmt="grid")
            return report_title, table
        else:
            return report_title, "No low stock items found."