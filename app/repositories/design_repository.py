"""Repository for RingDesign persistence."""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import RingDesign


class DesignRepository:
    def __init__(self, db: Session):
        self._db = db

    def create(
        self,
        *,
        user_id: int,
        design_payload: dict,
        summary: str,
        image_prompt: str,
        cautions: Optional[str] = None,
        reference_image_path: Optional[str] = None,
    ) -> RingDesign:
        design = RingDesign(
            user_id=user_id,
            design_payload=design_payload,
            summary=summary,
            image_prompt=image_prompt,
            cautions=cautions,
            reference_image_path=reference_image_path,
        )
        self._db.add(design)
        self._db.commit()
        self._db.refresh(design)
        return design

    def get(self, design_id: int) -> Optional[RingDesign]:
        return self._db.query(RingDesign).filter(RingDesign.id == design_id).first()

    def list_for_user(self, user_id: int) -> list[RingDesign]:
        return (
            self._db.query(RingDesign)
            .filter(RingDesign.user_id == user_id)
            .order_by(RingDesign.created_at.desc())
            .all()
        )

    def list_all(self) -> list[RingDesign]:
        return self._db.query(RingDesign).order_by(RingDesign.created_at.desc()).all()

    def set_generated_image(self, design_id: int, image_url: str) -> Optional[RingDesign]:
        design = self.get(design_id)
        if design is None:
            return None
        design.generated_image_url = image_url
        self._db.commit()
        self._db.refresh(design)
        return design

    def set_reference_image(self, design_id: int, reference_image_path: str) -> Optional[RingDesign]:
        design = self.get(design_id)
        if design is None:
            return None
        design.reference_image_path = reference_image_path
        self._db.commit()
        self._db.refresh(design)
        return design

    def delete(self, design_id: int) -> bool:
        design = self.get(design_id)
        if design is None:
            return False
        self._db.delete(design)
        self._db.commit()
        return True

    def delete_for_user(self, user_id: int) -> int:
        designs = self._db.query(RingDesign).filter(RingDesign.user_id == user_id).all()
        for design in designs:
            self._db.delete(design)
        self._db.commit()
        return len(designs)
