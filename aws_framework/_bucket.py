from boto3 import Session

from ._config import cfg, creds
from ._decorators import asyncify
from ._types import *


class S3Client:
    executor = ThreadPoolExecutor(max_workers=10)

    @property
    def client(self):
        return Session(**creds.dict()).client("s3")

    @asyncify
    def create_bucket(self, bucket_name: str) -> Awaitable[None]:
        return self.client.create_bucket(Bucket=bucket_name)

    @asyncify
    def delete_bucket(self, bucket_name: str) -> Awaitable[None]:
        return self.client.delete_bucket(Bucket=bucket_name)

    @asyncify
    def list_buckets(self) -> Awaitable[list[dict[str, Any]]]:
        return self.client.list_buckets()

    @asyncify
    def list_objects(self, bucket_name: str) -> Awaitable[list[dict[str, Any]]]:
        return self.client.list_objects(Bucket=bucket_name)

    @asyncify
    def put_object(
        self,
        bucket_name: str,
        key: str,
        body: bytes,
        content_type: str,
        acl: str = "public-read",
        content_disposition: str = "inline",
        **kwargs
    ) -> Awaitable[None]:
        return self.client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=body,
            ContentType=content_type,
            ACL=acl,
            ContentDisposition=content_disposition,
            **kwargs
        )

    @asyncify
    def generate_presigned_url(
        self,
        key: str,
        bucket_name: str = cfg.AWS_S3_BUCKET,
        expiration: int = 3600,
        **kwargs
    ) -> Awaitable[str]:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiration,
            **kwargs
        )

    @asyncify
    def get_object(self, bucket_name: str, key: str) -> Awaitable[dict[str, Any]]:
        return self.client.get_object(Bucket=bucket_name, Key=key)

    @asyncify
    def delete_object(self, bucket_name: str, key: str) -> Awaitable[None]:
        return self.client.delete_object(Bucket=bucket_name, Key=key)
