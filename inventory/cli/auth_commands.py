import os
import json
from ..services import UserService

class AuthCommands:
    """Commands for authentication and user management"""
    
    def __init__(self, session):
        self.user_service = UserService(session)
        self.session_file = os.path.join(os.path.expanduser("~"), ".inventory_session")
    
    def _save_session(self, user):
        """Save user session to file"""
        session_data = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f)
    
    def _load_session(self):
        """Load user session from file"""
        if not os.path.exists(self.session_file):
            return None
            
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
                
            # Verify user exists
            user = self.user_service.get_user_by_id(session_data.get("user_id"))
            if user:
                return session_data
        except:
            pass
            
        return None
    
    def _clear_session(self):
        """Clear user session"""
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
    
    def get_current_user(self):
        """Get current logged in user"""
        session = self._load_session()
        if not session:
            return None
            
        return self.user_service.get_user_by_id(session.get("user_id"))
    
    def login(self, args):
        """Log in a user"""
        if not args.username or not args.password:
            print("Error: Username and password are required")
            return False
        
        user = self.user_service.authenticate(args.username, args.password)
        if not user:
            print("Error: Invalid username or password")
            return False
        
        self._save_session(user)
        print(f"Logged in as {user.username} ({user.role})")
        return True
    
    def logout(self, args):
        """Log out current user"""
        self._clear_session()
        print("Logged out successfully")
        return True
    
    def create_user(self, args):
        """Create a new user"""
        # Check if current user is admin
        current_user = self.get_current_user()
        if not current_user or current_user.role != 'admin':
            print("Error: Admin privileges required")
            return False
        
        try:
            user = self.user_service.create_user(
                username=args.username,
                password=args.password,
                email=args.email,
                role=args.role
            )
            print(f"User {user.username} created successfully")
            return True
        except ValueError as e:
            print(f"Error: {str(e)}")
            return False
    
    def list_users(self, args):
        """List all users"""
        # Check if current user is admin
        current_user = self.get_current_user()
        if not current_user or current_user.role != 'admin':
            print("Error: Admin privileges required")
            return False
        
        users = self.user_service.get_all_users()
        if not users:
            print("No users found")
            return True
        
        print("\nUsers:")
        print("=" * 60)
        print(f"{'ID':<5} {'Username':<15} {'Role':<10} {'Email':<25} {'Last Login'}")
        print("-" * 60)
        
        for user in users:
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
            print(f"{user.user_id:<5} {user.username:<15} {user.role:<10} {user.email or '':<25} {last_login}")
        
        print("=" * 60)
        return True