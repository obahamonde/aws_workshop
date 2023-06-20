from typing import *

from pydantic import BaseModel  # pylint: disable=no-name-in-module
from pydantic import Field, HttpUrl  # pylint: disable=no-name-in-module

RuntimeL = Literal[
    "PYTHON_3','NODEJS_12','NODEJS_14','CORRETTO_8','CORRETTO_11','NODEJS_16','GO_1','DOTNET_6','PHP_81','RUBY_31"
]
ConfigurationSourceL = Literal["REPOSITORY", "API"]
SourceVersionTypeL = Literal["BRANCH", "TAG", "COMMIT_HASH"]
ImageRepositoryTypeL = Literal["ECR", "ECR_PUBLIC"]


class CodeConfigurationValuesT(BaseModel):
    runtime: RuntimeL = Field(..., alias="Runtime")
    build_command: Optional[str] = Field(None, alias="BuildCommand")
    start_command: Optional[str] = Field(None, alias="StartCommand")
    port: Optional[str] = Field(None, alias="Port")
    runtime_environment_variables: Optional[Dict[str, str]] = Field(
        None, alias="RuntimeEnvironmentVariables"
    )
    runtime_environment_secrets: Optional[Dict[str, str]] = Field(
        None, alias="RuntimeEnvironmentSecrets"
    )


class CodeConfigurationT(BaseModel):
    configuration_source: ConfigurationSourceL = Field(..., alias="ConfigurationSource")
    code_configuration_values: Optional[CodeConfigurationValuesT] = Field(
        ..., alias="CodeConfigurationValues"
    )


class SourceCodeVersionT(BaseModel):
    type: SourceVersionTypeL = Field(..., alias="Type")
    value: str = Field(..., alias="Value")


class CodeRepositoryT(BaseModel):
    repository_url: HttpUrl = Field(..., alias="RepositoryUrl")
    source_code_version: SourceCodeVersionT = Field(..., alias="SourceCodeVersion")
    code_configuration: CodeConfigurationT = Field(..., alias="CodeConfiguration")


class ImageConfigurationT(BaseModel):
    runtime_environment_variables: Optional[Dict[str, str]] = Field(
        None, alias="RuntimeEnvironmentVariables"
    )
    runtime_environment_secrets: Optional[Dict[str, str]] = Field(
        None, alias="RuntimeEnvironmentSecrets"
    )
    start_command: Optional[str] = Field(None, alias="StartCommand")
    port: Optional[str] = Field(None, alias="Port")
    image_repository_type: ImageRepositoryTypeL = Field(
        ..., alias="ImageRepositoryType"
    )


class ImageRepositoryT(BaseModel):
    image_identifier: str = Field(..., alias="ImageIdentifier")
    image_congifuration: Optional[ImageConfigurationT] = Field(
        None, alias="ImageConfiguration"
    )


class AuthenticationConfigurationT(BaseModel):
    connection_arn: Optional[str] = Field(None, alias="ConnectionArn")
    access_role_arn: Optional[str] = Field(None, alias="AccessRoleArn")


class InstanceConfigurationT(BaseModel):
    cpu: Optional[str] = Field(None, alias="Cpu")
    memory: Optional[str] = Field(None, alias="Memory")
    instance_role_arn: Optional[str] = Field(None, alias="InstanceRoleArn")
    instance_type: Optional[str] = Field(None, alias="InstanceType")


class TagT(BaseModel):
    key: Optional[str] = Field(None, alias="Key")
    value: Optional[str] = Field(None, alias="Value")


class EncryptionConfigurationT(BaseModel):
    kms_key: str = Field(..., alias="KmsKey")


class HealthCheckConfigurationT(BaseModel):
    protocol: Optional[str] = Field(None, alias="Protocol")
    path: Optional[str] = Field(None, alias="Path")
    interval: Optional[int] = Field(None, alias="Interval")
    timeout: Optional[int] = Field(None, alias="Timeout")
    healthy_threshold: Optional[int] = Field(None, alias="HealthyThreshold")
    unhealthy_threshold: Optional[int] = Field(None, alias="UnhealthyThreshold")


class EgressConfigurationT(BaseModel):
    egress_type: Optional[str] = Field(None, alias="EgressType")
    vpc_connector_arn: Optional[str] = Field(None, alias="VpcConnectorArn")


class IngressConfigurationT(BaseModel):
    is_publicly_accessible: Optional[bool] = Field(None, alias="IsPubliclyAccessible")


class NetworkConfigurationT(BaseModel):
    egress_configuration: Optional[EgressConfigurationT] = Field(
        None, alias="EgressConfiguration"
    )
    ingress_configuration: Optional[IngressConfigurationT] = Field(
        None, alias="IngressConfiguration"
    )


class ObservabilityConfigurationT(BaseModel):
    observability_enabled: Optional[bool] = Field(None, alias="ObservabilityEnabled")
    observability_configuration_arn: Optional[str] = Field(
        None, alias="ObservabilityConfigurationArn"
    )


class SourceConfigurationT(BaseModel):
    authentication_configuration: Optional[AuthenticationConfigurationT] = Field(
        None, alias="AuthenticationConfiguration"
    )
    auto_deployments_enabled: Optional[bool] = Field(
        None, alias="AutoDeploymentsEnabled"
    )
    code_repository: Optional[CodeRepositoryT] = Field(
        None, alias="CodeRepository"
    )  # =
    image_repository: Optional[ImageRepositoryT] = Field(
        None, alias="ImageRepository"
    )  # =
    instance_configuration: Optional[InstanceConfigurationT] = Field(
        None, alias="InstanceConfiguration"
    )
    tags: Optional[List[TagT]] = Field(None, alias="Tags")
    encryption_configuration: Optional[EncryptionConfigurationT] = Field(
        None, alias="EncryptionConfiguration"
    )
    health_check_configuration: Optional[HealthCheckConfigurationT] = Field(
        None, alias="HealthCheckConfiguration"
    )
    network_configuration: Optional[NetworkConfigurationT] = Field(
        None, alias="NetworkConfiguration"
    )
    observability_configuration: Optional[ObservabilityConfigurationT] = Field(
        None, alias="ObservabilityConfiguration"
    )

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.code_repository is None and self.image_repository is None:
            raise ValueError(
                "Either code_repository or image_repository must be specified"
            )
        if self.code_repository is not None and self.image_repository is not None:
            raise ValueError(
                "Only one of code_repository or image_repository can be specified"
            )
        if (
            self.code_repository is not None
            and self.code_repository.code_configuration is None
        ):
            raise ValueError(
                "code_configuration must be specified if code_repository is specified"
            )
        if (
            self.image_repository is not None
            and self.image_repository.image_congifuration is None
        ):
            raise ValueError(
                "image_congifuration must be specified if image_repository is specified"
            )
        if (
            self.code_repository is not None
            and self.code_repository.code_configuration.configuration_source == "API"
        ):
            if (
                self.code_repository.code_configuration.code_configuration_values
                is None
            ):
                raise ValueError(
                    "code_configuration_values must be specified if code_repository.configuration_source is API"
                )
            if (
                self.code_repository.code_configuration.code_configuration_values.runtime
                is None
            ):
                raise ValueError(
                    "runtime must be specified if code_repository.configuration_source is API"
                )
        if (
            self.image_repository is not None
            and self.image_repository.image_congifuration is not None
        ):
            if self.image_repository.image_congifuration.image_repository_type == "ECR":
                if (
                    self.image_repository.image_congifuration.runtime_environment_variables
                    is None
                ):
                    raise ValueError(
                        "runtime_environment_variables must be specified if image_repository.image_congifuration.image_repository_type is ECR"
                    )
                if (
                    self.image_repository.image_congifuration.runtime_environment_secrets
                    is None
                ):
                    raise ValueError(
                        "runtime_environment_secrets must be specified if image_repository.image_congifuration.image_repository_type is ECR"
                    )
                if self.image_repository.image_congifuration.start_command is None:
                    raise ValueError(
                        "start_command must be specified if image_repository.image_congifuration.image_repository_type is ECR"
                    )
                if self.image_repository.image_congifuration.port is None:
                    raise ValueError(
                        "port must be specified if image_repository.image_congifuration.image_repository_type is ECR"
                    )
            if (
                self.image_repository.image_congifuration.image_repository_type
                == "ECR_PUBLIC"
            ):
                if (
                    self.image_repository.image_congifuration.runtime_environment_variables
                    is None
                ):
                    raise ValueError(
                        "runtime_environment_variables must be specified if image_repository.image_congifuration.image_repository_type is ECR_PUBLIC"
                    )
                if (
                    self.image_repository.image_congifuration.runtime_environment_secrets
                    is None
                ):
                    raise ValueError(
                        "runtime_environment_secrets must be specified if image_repository.image_congifuration.image_repository_type is ECR_PUBLIC"
                    )
                if self.image_repository.image_congifuration.start_command is None:
                    raise ValueError(
                        "start_command must be specified if image_repository.image_congifuration.image_repository_type is ECR_PUBLIC"
                    )


class ServiceConfigurationT(BaseModel):
    service_name: str = Field(..., alias="ServiceName")
    source_configuration: SourceConfigurationT = Field(..., alias="SourceConfiguration")
