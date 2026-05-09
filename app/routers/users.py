"""User management routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/users", tags=["Users"])


def _serialize_user(user, *, include_updated_at: bool = True) -> dict:
    payload = {
        "user_id": user.id,
        "customer_id": user.customer_id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
    }
    if include_updated_at:
        payload["updated_at"] = user.updated_at.isoformat()
    return payload


@router.get("/get", summary="Get user by customer ID")
async def get_user(
    customer_id: str = Query(..., description="Customer ID"),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    user = repo.get_by_customer_id(customer_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with customer_id {customer_id} not found",
        )
    return _serialize_user(user)


@router.get("/all", summary="List all users")
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    users = repo.list(skip=skip, limit=limit)
    return {
        "count": len(users),
        "users": [_serialize_user(user, include_updated_at=False) for user in users],
    }
