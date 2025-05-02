from datetime import datetime
from sqlalchemy import and_, between
from ..models import Transaction, Product, Warehouse, User
from .base_repository import BaseRepository

class TransactionRepository(BaseRepository):
    """Repository for Transaction model"""
    
    def __init__(self, session):
        super().__init__(session, Transaction)
    
    def get_transactions_by_date_range(self, start_date, end_date):
        return (self.session.query(Transaction, Product, Warehouse, User)
                .join(Product)
                .join(Warehouse)
                .join(User)
                .filter(between(Transaction.timestamp, start_date, end_date))
                .all())
    
    def get_transactions_by_product(self, product_id):
        return self.session.query(Transaction).filter(
            Transaction.product_id == product_id
        ).all()
    
    def get_transactions_by_warehouse(self, warehouse_id):
        return self.session.query(Transaction).filter(
            Transaction.warehouse_id == warehouse_id
        ).all()
    
    def get_transactions_by_barcode(self, barcode):
        return (self.session.query(Transaction)
                .join(Product)
                .filter(Product.barcode == barcode)
                .all())