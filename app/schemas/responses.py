"""Response schemas returned by the API."""

from typing import Optional

from pydantic import BaseModel, Field


class DesignBrief(BaseModel):
    image_prompt: str
    cautions: Optional[str] = None


class ImageUploadResponse(BaseModel):
    image_url: str
    filename: str


class RingDesignResponse(BaseModel):
    design_id: int = Field(..., description="Design ID for image generation and tracking")
    summary: str
    image_prompt: str
    cautions: Optional[str] = None


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., description="The image generation prompt")


class ImageGenerateResponse(BaseModel):
    image_url: str = Field(..., description="S3 URL of the generated image")
    prompt: str = Field(..., description="The prompt that was submitted")
