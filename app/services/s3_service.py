"""S3 client wrapper — bucket bootstrap and object upload."""

from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_s3_client = None


def _get_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
    return _s3_client


def ensure_bucket_exists() -> None:
    """Create the S3 bucket if it does not already exist."""
    client = _get_client()
    bucket = settings.s3_bucket_name
    region = settings.aws_region

    try:
        client.head_bucket(Bucket=bucket)
        return
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            logger.info("Creating S3 bucket %s in %s", bucket, region)
            if region == "us-east-1":
                client.create_bucket(Bucket=bucket)
            else:
                client.create_bucket(
                    Bucket=bucket,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            return
        if code == "403":
            raise RuntimeError(
                f"S3 bucket '{bucket}' exists but is owned by a different AWS account. "
                "Choose a globally-unique S3_BUCKET_NAME."
            ) from exc
        raise


def upload_image(key: str, image_bytes: bytes, content_type: str = "image/png") -> str:
    """Upload bytes to S3 and return the public HTTPS URL."""
    client = _get_client()
    client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=image_bytes,
        ContentType=content_type,
    )
    return f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"
