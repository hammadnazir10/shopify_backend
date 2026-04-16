from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from app.config import settings

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
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            if region == "us-east-1":
                client.create_bucket(Bucket=bucket)
            else:
                client.create_bucket(
                    Bucket=bucket,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
        else:
            raise


def upload_image(filename: str, image_bytes: bytes, content_type: str = "image/png") -> str:
    """Upload image bytes to S3 and return the public HTTPS URL."""
    client = _get_client()
    bucket = settings.s3_bucket_name
    region = settings.aws_region

    client.put_object(
        Bucket=bucket,
        Key=filename,
        Body=image_bytes,
        ContentType=content_type,
    )

    return f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"
