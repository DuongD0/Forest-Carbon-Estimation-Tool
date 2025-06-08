from sqlalchemy.orm import Session
import uuid
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_by_auth0_sub(self, db: Session, *, auth0_sub: str) -> User | None:
        return db.query(User).filter(User.id == auth0_sub).first()

    def create_from_auth0(self, db: Session, *, user_in: User) -> User:
        db_obj = User(
            id=user_in.id,
            email=user_in.email,
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user = CRUDUser(User) 