from __future__ import annotations

from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from apps.api.config import settings


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name="us-east-1",
    )


def ensure_bucket_exists(bucket: str) -> None:
    client = _client()
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)


def upload_bytes(key: str, content: bytes, content_type: str | None = None) -> str:
    ensure_bucket_exists(settings.s3_bucket)
    client = _client()
    extra_args = {"ContentType": content_type} if content_type else None
    client.put_object(Bucket=settings.s3_bucket, Key=key, Body=content, **(extra_args or {}))
    return f"{settings.s3_endpoint}/{settings.s3_bucket}/{key}"


def upload_stream(key: str, body: BinaryIO, content_type: str | None = None) -> str:
    ensure_bucket_exists(settings.s3_bucket)
    client = _client()
    extra_args = {"ContentType": content_type} if content_type else None
    client.upload_fileobj(body, settings.s3_bucket, key, ExtraArgs=extra_args or {})
    return f"{settings.s3_endpoint}/{settings.s3_bucket}/{key}"


def key_from_url(url: str) -> str | None:
    endpoint = settings.s3_endpoint.rstrip("/")
    bucket = settings.s3_bucket.strip("/")
    prefix = f"{endpoint}/{bucket}/"
    if not url.startswith(prefix):
        return None
    return url[len(prefix) :]


def download_bytes(key: str) -> bytes:
    ensure_bucket_exists(settings.s3_bucket)
    client = _client()
    response = client.get_object(Bucket=settings.s3_bucket, Key=key)
    body = response["Body"].read()
    return body if isinstance(body, bytes) else bytes(body)
