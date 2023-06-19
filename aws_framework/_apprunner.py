import base64

from boto3 import Session
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from ._apprunnerTypes import ServiceConfigurationT
from ._config import cfg, creds
from ._decorators import asyncify
from ._types import *
from .odm import Field, NoSQLModel


class AppRunner(LazyProxy[Session]):
    executor = ThreadPoolExecutor(max_workers=10)

    def __load__(self):
        return Session(**creds.dict()).client(
            "apprunner", region_name=creds.AWS_DEFAULT_REGION
        )

    @asyncify
    def create_github_connection(self, name:str) -> Awaitable[JSON]:
        response = self.__load__().create_connection(
            ConnectionName=name,
            ProviderType="GITHUB"
        )
        return cast(Awaitable[JSON], response)

    @asyncify
    def create_service(self, service: ServiceConfigurationT)-> Awaitable[JSON]:
        if service.source_configuration.code_repository:
            source_configuration = {
                "CodeRepository": {
                    "RepositoryUrl": service.source_configuration.code_repository,
                }
            }   
        else:
            source_configuration = {
                "ImageRepository": {
                    "ImageIdentifier": service.source_configuration.image_repository,
                }
            }
        response = self.__load__().create_service(  
            ServiceName=service.service_name,
            SourceConfiguration=source_configuration,   
            InstanceConfiguration={
                "Cpu": service.source_configuration.instance_configuration.cpu,
                "Memory": service.source_configuration.instance_configuration.memory,
                "InstanceRoleArn": service.source_configuration.instance_configuration.instance_role_arn,
                "InstanceType": service.source_configuration.instance_configuration.instance_type,
            },
            Tags=service.source_configuration.tags,
            EncryptionConfiguration=service.source_configuration.encryption_configuration,
            HealthCheckConfiguration=service.source_configuration.health_check_configuration,
            AutoScalingConfigurationArn=service.source_configuration.auto_scaling_configuration_arn,
            CodeConfiguration=service.source_configuration.code_repository.code_configuration,
            ImageConfiguration=service.source_configuration.image_repository.image_configuration,
        )
        return cast(Awaitable[JSON], response)
class Ecr(LazyProxy[Session]):
    executor = ThreadPoolExecutor(max_workers=10)

    def __load__(self):
        return Session(**creds.dict()).client(
            "ecr", region_name=creds.AWS_DEFAULT_REGION
        )

    @asyncify
    def get_login_password(self) -> Awaitable[AuthResult]:
        response = self.__load__().get_authorization_token()
        token = response["authorizationData"][0]["authorizationToken"]
        decoded = base64.b64decode(token).decode()
        username, password = decoded.split(":")
        registry = response["authorizationData"][0]["proxyEndpoint"]
        return cast(Awaitable[AuthResult], AuthResult(username=username, password=password, registry=registry))