"""Repository for User persistence."""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_customer_id(self, customer_id: str) -> Optional[User]:
        return self._db.query(User).filter(User.customer_id == customer_id).first()

    def list(self, skip: int = 0, limit: int = 10) -> list[User]:
        return self._db.query(User).offset(skip).limit(limit).all()

    def get_or_create(self, customer_id: str, name: str, email: Optional[str] = None) -> User:
        user = self.get_by_customer_id(customer_id)
        if user is None:
            user = User(customer_id=customer_id, name=name, email=email)
            self._db.add(user)
            self._db.commit()
            self._db.refresh(user)
            return user

        if email and user.email != email:
            user.email = email
            self._db.commit()
            self._db.refresh(user)
        return user
