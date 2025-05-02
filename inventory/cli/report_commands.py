from datetime import datetime
from ..services import ReportService

class ReportCommands:
    """Commands for generating reports"""
    
    def __init__(self, session, auth_commands):
        self.report_service = ReportService(session)
        self.auth_commands = auth_commands
    
    def inventory_report(self, args):
        """Generate inventory report"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        # Generate report
        title, report = self.report_service.generate_inventory_report(args.warehouse)
        
        # Display report
        print("\n" + "=" * 80)
        print(f"{title}")
        print("=" * 80)
        print(report)
        
        return True
    
    def transaction_report(self, args):
        """Generate transaction report"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        # Parse dates
        start_date = None
        end_date = None
        
        if args.date_from:
            try:
                start_date = datetime.strptime(args.date_from, '%Y-%m-%d')
            except ValueError:
                print("Error: Invalid date format for date-from. Use YYYY-MM-DD")
                return False
                
        if args.date_to:
            try:
                end_date = datetime.strptime(args.date_to, '%Y-%m-%d')
                # Set to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                print("Error: Invalid date format for date-to. Use YYYY-MM-DD")
                return False
        
        # Generate report
        title, report = self.report_service.generate_transaction_report(
            start_date=start_date,
            end_date=end_date,
            product_id=args.product,
            warehouse_id=args.warehouse
        )
        
        # Display report
        print("\n" + "=" * 80)
        print(f"{title}")
        print("=" * 80)
        print(report)
        
        return True
    
    def low_stock_report(self, args):
        """Generate low stock report"""
        # Check if user is logged in
        current_user = self.auth_commands.get_current_user()
        if not current_user:
            print("Error: You must be logged in")
            return False
        
        # Generate report
        title, report = self.report_service.generate_low_stock_report(args.threshold)
        
        # Display report
        print("\n" + "=" * 80)
        print(f"{title}")
        print("=" * 80)
        print(report)
        
        return True