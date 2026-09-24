import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.enums import UserRole

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)
    
    def get_by_email(self, email: str, school_id: uuid.UUID | None = None) -> User | None:
        query = self.db.query(User).filter(User.email == email)
        if school_id is not None:
            query = query.filter(User.school_id == school_id)
        return query.first()
    
    def create(
        self,
        *,
        email: str,
        hashed_password: str,
        full_name: str,
        role:UserRole,
        school_id: uuid.UUID | None,
    ) -> User:
        user =User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            school_id=school_id
        )
        self.db.add(user)
        self.db.flush() # populate user.id without commiting the transcation
        return user