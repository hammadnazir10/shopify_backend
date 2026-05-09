"""User management routes."""

import asyncio
from fastapi import APIRouter, Query, HTTPException

from app.database import get_or_create_user, SessionLocal, User


router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get(
    "/get",
    summary="Get user by customer ID",
    description="Retrieves user information by customer ID",
)
async def get_user(
    customer_id: str = Query(..., description="Customer ID"),
):
    """Get user details by customer ID."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.customer_id == customer_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with customer_id {customer_id} not found")
        
        return {
            "user_id": user.id,
            "customer_id": user.customer_id,
            "name": user.name,            "email": user.email,            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }
    finally:
        db.close()


@router.get(
    "/all",
    summary="List all users",
    description="Returns a list of all users in the system",
)
async def list_all_users(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """Get all users with pagination."""
    db = SessionLocal()
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return {
            "count": len(users),
            "users": [
                {
                    "user_id": user.id,
                    "customer_id": user.customer_id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at.isoformat(),
                }
                for user in users
            ]
        }
    finally:
        db.close()
