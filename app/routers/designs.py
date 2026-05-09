"""Ring design management routes."""

import asyncio
from fastapi import APIRouter, Query, HTTPException, Path as PathParam

from app.database import (
    SessionLocal,
    RingDesign,
    User,
    get_design,
    get_user_designs,
    get_user_by_customer_id,
)


router = APIRouter(prefix="/api/designs", tags=["Designs"])


@router.get(
    "/customer/{customer_id}",
    summary="Get all designs for a customer",
    description="Retrieves all ring designs for a user identified by customer_id",
)
async def get_designs_by_customer(
    customer_id: str = PathParam(..., description="Customer ID"),
):
    """Get all designs for a user by customer_id."""
    try:
        user = await asyncio.to_thread(get_user_by_customer_id, customer_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with customer_id {customer_id} not found")
        designs = await asyncio.to_thread(get_user_designs, user.id)
        
        return {
            "customer_id": customer_id,
            "count": len(designs),
            "designs": [
                {
                    "id": design.id,
                    "customer_id": user.customer_id,
                    "design_payload": design.design_payload,
                    "summary": design.summary,
                    "image_prompt": design.image_prompt,
                    "cautions": design.cautions,
                    "reference_image_path": design.reference_image_path,
                    "generated_image_url": design.generated_image_url,
                    "created_at": design.created_at.isoformat(),
                    "updated_at": design.updated_at.isoformat(),
                }
                for design in designs
            ]
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error retrieving designs for customer_id {customer_id}: {exc}")



@router.get(
    "/{design_id}",
    summary="Get a specific design",
    description="Retrieves a single ring design by ID",
)
async def get_design_by_id(
    design_id: int = PathParam(..., description="Design ID"),
):
    """Get a specific design by ID."""
    try:
        design = await asyncio.to_thread(get_design, design_id)
        
        if not design:
            raise HTTPException(status_code=404, detail=f"Design with ID {design_id} not found")
        
        return {
            "id": design.id,
            "user_id": design.user_id,
            "customer_id": design.user.customer_id if design.user else None,
            "design_payload": design.design_payload,
            "summary": design.summary,
            "image_prompt": design.image_prompt,
            "cautions": design.cautions,
            "reference_image_path": design.reference_image_path,
            "generated_image_url": design.generated_image_url,
            "created_at": design.created_at.isoformat(),
            "updated_at": design.updated_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error retrieving design: {exc}")


@router.delete(
    "/{design_id}",
    summary="Delete a design",
    description="Deletes a ring design by ID",
)
async def delete_design(
    design_id: int = PathParam(..., description="Design ID"),
):
    """Delete a design by ID."""
    db = SessionLocal()
    try:
        design = db.query(RingDesign).filter(RingDesign.id == design_id).first()
        
        if not design:
            raise HTTPException(status_code=404, detail=f"Design with ID {design_id} not found")
        
        db.delete(design)
        db.commit()
        
        return {
            "message": f"Design {design_id} deleted successfully",
            "deleted_design_id": design_id,
        }
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting design: {exc}")
    finally:
        db.close()


@router.delete(
    "/customer/{customer_id}",
    summary="Delete all designs for a customer",
    description="Deletes all ring designs for a user identified by customer_id",
)
async def delete_customer_designs(
    customer_id: str = PathParam(..., description="Customer ID"),
):
    """Delete all designs for a user by customer_id."""
    db = SessionLocal()
    try:
        user = await asyncio.to_thread(get_user_by_customer_id, customer_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with customer_id {customer_id} not found")
        
        designs = db.query(RingDesign).filter(RingDesign.user_id == user.id).all()
        count = len(designs)
        
        for design in designs:
            db.delete(design)
        
        db.commit()
        
        return {
            "message": f"Deleted {count} designs for customer_id {customer_id}",
            "customer_id": customer_id,
            "deleted_count": count,
        }
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting designs for customer_id {customer_id}: {exc}")
    finally:
        db.close()
