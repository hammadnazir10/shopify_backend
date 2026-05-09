"""Ring design management routes."""

from fastapi import APIRouter, Depends, HTTPException, Path as PathParam, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.design_repository import DesignRepository
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/designs", tags=["Designs"])


def _serialize_design(design, *, customer_id: str | None = None) -> dict:
    customer = customer_id if customer_id is not None else (
        design.user.customer_id if design.user else None
    )
    return {
        "id": design.id,
        "user_id": design.user_id,
        "customer_id": customer,
        "design_payload": design.design_payload,
        "summary": design.summary,
        "image_prompt": design.image_prompt,
        "cautions": design.cautions,
        "reference_image_path": design.reference_image_path,
        "generated_image_url": design.generated_image_url,
        "created_at": design.created_at.isoformat(),
        "updated_at": design.updated_at.isoformat(),
    }


@router.get("/customer/{customer_id}", summary="Get all designs for a customer")
async def get_designs_by_customer(
    customer_id: str = PathParam(..., description="Customer ID"),
    db: Session = Depends(get_db),
):
    user = UserRepository(db).get_by_customer_id(customer_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with customer_id {customer_id} not found",
        )

    designs = DesignRepository(db).list_for_user(user.id)
    return {
        "customer_id": customer_id,
        "count": len(designs),
        "designs": [_serialize_design(d, customer_id=customer_id) for d in designs],
    }


@router.get("/{design_id}", summary="Get a specific design")
async def get_design_by_id(
    design_id: int = PathParam(..., description="Design ID"),
    db: Session = Depends(get_db),
):
    design = DesignRepository(db).get(design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Design with ID {design_id} not found",
        )
    return _serialize_design(design)


@router.delete("/{design_id}", summary="Delete a design")
async def delete_design(
    design_id: int = PathParam(..., description="Design ID"),
    db: Session = Depends(get_db),
):
    deleted = DesignRepository(db).delete(design_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Design with ID {design_id} not found",
        )
    return {
        "message": f"Design {design_id} deleted successfully",
        "deleted_design_id": design_id,
    }


@router.delete("/customer/{customer_id}", summary="Delete all designs for a customer")
async def delete_customer_designs(
    customer_id: str = PathParam(..., description="Customer ID"),
    db: Session = Depends(get_db),
):
    user = UserRepository(db).get_by_customer_id(customer_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with customer_id {customer_id} not found",
        )

    deleted_count = DesignRepository(db).delete_for_user(user.id)
    return {
        "message": f"Deleted {deleted_count} designs for customer_id {customer_id}",
        "customer_id": customer_id,
        "deleted_count": deleted_count,
    }
