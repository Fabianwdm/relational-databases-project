from sqlalchemy.exc import SQLAlchemyError

class BaseRepository:
    """Base repository class with common database operations"""
    
    def __init__(self, session, model_class):
        self.session = session
        self.model_class = model_class
    
    def get_all(self):
        """Get all records of the model"""
        return self.session.query(self.model_class).all()
    
    def get_by_id(self, id_value):
        """Get a record by its primary key"""
        primary_key = self.model_class.__mapper__.primary_key[0].name
        return self.session.query(self.model_class).filter(
            getattr(self.model_class, primary_key) == id_value
        ).first()
    
    def create(self, **kwargs):
        """Create a new record"""
        try:
            instance = self.model_class(**kwargs)
            self.session.add(instance)
            self.session.commit()
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def update(self, id_value, **kwargs):
        """Update a record by its primary key"""
        try:
            primary_key = self.model_class.__mapper__.primary_key[0].name
            instance = self.session.query(self.model_class).filter(
                getattr(self.model_class, primary_key) == id_value
            ).first()
            
            if instance:
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                
                self.session.commit()
                return instance
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def delete(self, id_value):
        """Delete a record by its primary key"""
        try:
            primary_key = self.model_class.__mapper__.primary_key[0].name
            instance = self.session.query(self.model_class).filter(
                getattr(self.model_class, primary_key) == id_value
            ).first()
            
            if instance:
                self.session.delete(instance)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def get_by_filter(self, **filters):
        """Get records by filter criteria"""
        query = self.session.query(self.model_class)
        
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
                
        return query.all()