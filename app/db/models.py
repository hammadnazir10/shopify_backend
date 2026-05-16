"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.schemas.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    role = Column(
        String(20),
        nullable=False,
        default=UserRole.customer.value,
        server_default=text("'customer'"),
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    designs = relationship(
        "RingDesign",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} customer_id={self.customer_id!r} role={self.role!r}>"


class RingDesign(Base):
    __tablename__ = "ring_designs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    design_payload = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    image_prompt = Column(Text, nullable=True)
    cautions = Column(Text, nullable=True)

    reference_image_path = Column(String(500), nullable=True)
    generated_image_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="designs")

    def __repr__(self) -> str:
        return f"<RingDesign id={self.id} user_id={self.user_id}>"
