from boto3 import Session
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from ._config import cfg, creds
from ._decorators import asyncify
from ._types import *
from .odm import Field, NoSQLModel


class ConnectionParams(BaseModel):
    repo: str
    image: str
    name: str


class ServiceParams(BaseModel):
    name: str
    repo: str
    image: str
    port: int


class AppRunner(LazyProxy[Session]):
    executor = ThreadPoolExecutor(max_workers=10)

    def __load__(self):
        return Session(**creds.dict()).client(
            "apprunner", region_name=creds.AWS_DEFAULT_REGION
        )

    @asyncify
    def create_github_connection(self, conn: ConnectionParams) -> Awaitable[JSON]:
        response = self.__load__().create_connection(
            ConnectionName=conn.name,
            ProviderType="GITHUB",
            ConnectionParameters={
                "SourceCodeRepository": conn.repo,
            },
        )
        return cast(Awaitable[JSON], response)

    @asyncify
    def create_service(self, service: ServiceParams) -> Awaitable[JSON]:
        response = self.__load__().create_service(
            ServiceName=service.name,
            SourceConfiguration={
                "CodeRepository": {
                    "RepositoryUrl": service.repo,
                },
                "ImageRepository": {
                    "ImageIdentifier": service.image,
                },
            },
            InstanceConfiguration={
                "Cpu": "1 vCPU",
                "Memory": "2 GB",
            },
            Tags={
                "Name": service.name,
            },
            Port=service.port,
        )
        return cast(Awaitable[JSON], response)
