import hashlib
import os
from ..repositories import BaseRepository
from ..models import User

class UserService:
    """Service class for user management"""
    
    def __init__(self, session):
        self.user_repo = BaseRepository(session, User)
        self.session = session
    
    def _hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = os.urandom(32)  # Generate new salt if none provided
            
        # Hash password with salt
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # Number of iterations
        )
        
        # Return hash and salt as hex strings
        return salt.hex() + hash_obj.hex(), salt
    
    def _verify_password(self, stored_hash, password):
        """Verify a password against a stored hash"""
        # Extract salt from stored hash (first 64 chars = 32 bytes as hex)
        salt = bytes.fromhex(stored_hash[:64])
        
        # Hash the provided password with extracted salt
        new_hash, _ = self._hash_password(password, salt)
        
        # Compare
        return new_hash == stored_hash
    
    def authenticate(self, username, password):
        """Authenticate a user by username and password"""
        users = self.user_repo.get_by_filter(username=username)
        
        if not users:
            return None
            
        user = users[0]
        
        if self._verify_password(user.password_hash, password):
            # Update last login time
            from datetime import datetime
            self.user_repo.update(user.user_id, last_login=datetime.utcnow())
            return user
            
        return None
        
    def create_user(self, username, password, email=None, role='staff'):
        """Create a new user"""
        # Check if username already exists
        if self.user_repo.get_by_filter(username=username):
            raise ValueError(f"Username '{username}' already exists")
            
        # Hash password
        password_hash, _ = self._hash_password(password)
        
        # Create user
        return self.user_repo.create(
            username=username,
            password_hash=password_hash,
            email=email,
            role=role
        )
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        # Handle password update separately
        if 'password' in kwargs:
            password_hash, _ = self._hash_password(kwargs['password'])
            kwargs['password_hash'] = password_hash
            del kwargs['password']
            
        return self.user_repo.update(user_id, **kwargs)
    
    def get_all_users(self):
        """Get all users"""
        return self.user_repo.get_all()
    
    def get_user_by_id(self, user_id):
        """Get a user by ID"""
        return self.user_repo.get_by_id(user_id)
    
    def delete_user(self, user_id):
        """Delete a user"""
        return self.user_repo.delete(user_id)