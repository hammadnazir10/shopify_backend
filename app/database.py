"""Database connection and session management."""

from sqlalchemy import create_engine, Column, String, DateTime, Integer, ForeignKey, JSON, Text, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import settings

# Create engine
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class User(Base):
    """User model for storing customer information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    designs = relationship("RingDesign", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, customer_id={self.customer_id}, name={self.name}, email={self.email})>"


class RingDesign(Base):
    """Ring design model for storing user's ring design submissions."""
    __tablename__ = "ring_designs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Full questionnaire payload
    design_payload = Column(JSON, nullable=True)

    # Design metadata
    summary = Column(Text, nullable=True)
    image_prompt = Column(Text, nullable=True)
    cautions = Column(Text, nullable=True)
    
    # Reference image (local temp path)
    reference_image_path = Column(String(500), nullable=True)
    
    # Generated image URL
    generated_image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="designs")

    def __repr__(self):
        return f"<RingDesign(id={self.id}, user_id={self.user_id})>"


def migrate_ring_design_schema():
    """Bring the ring_designs table in line with the simplified payload schema."""
    inspector = inspect(engine)
    if not inspector.has_table("ring_designs"):
        return

    columns = {column["name"] for column in inspector.get_columns("ring_designs")}

    with engine.begin() as connection:
        if "design_payload" not in columns:
            connection.execute(text("ALTER TABLE ring_designs ADD COLUMN design_payload JSON"))

        for column_name in (
            "style_family",
            "metal",
            "style_direction",
            "setting",
            "stone_name",
            "stone_color",
            "fit_label",
            "generated_image_local_path",
            "generated_model",
        ):
            if column_name in columns:
                connection.execute(text(f'ALTER TABLE ring_designs DROP COLUMN IF EXISTS "{column_name}"'))


def create_tables():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    migrate_ring_design_schema()
    print("✓ Database tables created/verified")


def get_db():
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_user(customer_id: str, name: str, email: str = None):
    """Get existing user or create new one."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.customer_id == customer_id).first()
        if not user:
            user = User(customer_id=customer_id, name=name, email=email)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update email if provided and different
            if email and user.email != email:
                user.email = email
                db.commit()
                db.refresh(user)
        return user
    finally:
        db.close()


def generate_payload_summary(payload: dict) -> str:
    """Generate a human-readable summary from design payload for dashboard display."""
    parts = []
    
    # Jewelry type
    if payload.get("jewelry_type"):
        parts.append(payload["jewelry_type"])
    
    # Style direction
    if payload.get("style_direction"):
        parts.append(payload["style_direction"])
    
    # Style family
    if payload.get("style_family"):
        parts.append(payload["style_family"])
    
    # Metal
    if payload.get("metal"):
        parts.append(payload["metal"])
    
    # Setting
    if payload.get("setting"):
        parts.append(payload["setting"])
    
    # Stone choice
    if payload.get("chosen_stone_name"):
        parts.append(f"with {payload['chosen_stone_name']}")
    
    # Wear frequency
    if payload.get("wear_frequency"):
        parts.append(f"for {payload['wear_frequency'].lower()} wear")
    
    # Final preferences
    if payload.get("final_preferences"):
        parts.append(f"({payload['final_preferences']})")
    
    return " • ".join(parts) if parts else "Custom ring design"


def create_ring_design(user_id: int, design_payload: dict, summary: str, image_prompt: str,
                       cautions: str = None, reference_image_path: str = None):
    """Create a new ring design record for a user."""
    db = SessionLocal()
    try:
        design = RingDesign(
            user_id=user_id,
            design_payload=design_payload,
            summary=summary,
            image_prompt=image_prompt,
            cautions=cautions,
            reference_image_path=reference_image_path,
        )
        db.add(design)
        db.commit()
        db.refresh(design)
        return design
    finally:
        db.close()


def update_design_image(design_id: int, image_url: str):
    """Update a design with the generated image URL."""
    db = SessionLocal()
    try:
        design = db.query(RingDesign).filter(RingDesign.id == design_id).first()
        if design:
            design.generated_image_url = image_url
            db.commit()
            db.refresh(design)
        return design
    finally:
        db.close()


def update_reference_image_path(design_id: int, reference_image_path: str):
    """Update a design with the reference image path."""
    db = SessionLocal()
    try:
        design = db.query(RingDesign).filter(RingDesign.id == design_id).first()
        if design:
            design.reference_image_path = reference_image_path
            db.commit()
            db.refresh(design)
        return design
    finally:
        db.close()


def get_user_designs(user_id: int):
    """Get all designs for a user."""
    db = SessionLocal()
    try:
        designs = db.query(RingDesign).filter(RingDesign.user_id == user_id).order_by(RingDesign.created_at.desc()).all()
        return designs
    finally:
        db.close()


def get_user_by_customer_id(customer_id: str):
    """Return a User by their customer_id string."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.customer_id == customer_id).first()
    finally:
        db.close()


def get_design(design_id: int):
    """Get a specific design by ID."""
    db = SessionLocal()
    try:
        design = db.query(RingDesign).filter(RingDesign.id == design_id).first()
        return design
    finally:
        db.close()
