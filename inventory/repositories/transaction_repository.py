from datetime import datetime
from sqlalchemy import and_, between
from ..models import Transaction, Product, Warehouse, User
from .base_repository import BaseRepository

class TransactionRepository(BaseRepository):
    """Repository for Transaction model"""
    
    def __init__(self, session):
        super().__init__(session, Transaction)
    
    def get_transactions_by_date_range(self, start_date, end_date):
        """Get transactions within a date range"""
        return (self.session.query(Transaction, Product, Warehouse, User)
                .join(Product)
                .join(Warehouse)
                .join(User)
                .filter(between(Transaction.timestamp, start_date, end_date))
                .all())
    
    def get_transactions_by_product(self, product_id):
        """Get all transactions for a specific product"""
        return self.session.query(Transaction).filter(
            Transaction.product_id == product_id
        ).all()
    
    def get_transactions_by_warehouse(self, warehouse_id):
        """Get all transactions for a specific warehouse"""
        return self.session.query(Transaction).filter(
            Transaction.warehouse_id == warehouse_id
        ).all()
    
    def get_transactions_by_barcode(self, barcode):
        """Get all transactions for a product with the given barcode"""
        return (self.session.query(Transaction)
                .join(Product)
                .filter(Product.barcode == barcode)
                .all())