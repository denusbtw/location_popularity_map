import boto3
from botocore.client import Config as BotoConfig
from django.conf import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    config=BotoConfig(
        signature_version="s3v4",
    ),
)
