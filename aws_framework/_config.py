import base64
import json

from pydantic import BaseConfig, BaseSettings, Field


class AWSCredentials(BaseSettings):
    """AWS credentials for boto3"""

    class Config(BaseConfig):
        """Extra config for AWS credentials"""

        env_file = ".env"
        env_file_encoding = "utf-8"

    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION: str = Field(..., env="AWS_DEFAULT_REGION")
    secret: str = Field(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.secret = base64.b64encode(json.dumps(self.dict()).encode("utf-8")).decode(
            "utf-8"
        )

    def dict(self):
        return {
            "aws_access_key_id": self.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": self.AWS_SECRET_ACCESS_KEY,
            "region_name": self.AWS_DEFAULT_REGION,
        }


class Configuration(BaseSettings):
    class Config(BaseConfig):
        """Extra config for AWS credentials"""

        env_file = ".env"
        env_file_encoding = "utf-8"

    AWS_LAMBDA_ROLE: str = Field(..., env="AWS_LAMBDA_ROLE")
    AWS_S3_BUCKET: str = Field(..., env="AWS_S3_BUCKET")
    DOCKER_URL: str = Field(..., env="DOCKER_URL")
    AWS_ECR_URI: str = Field(..., env="AWS_ECR_URI")
    AWS_COGNITO_USER_POOL_ID: str = Field(..., env="AWS_COGNITO_USER_POOL_ID")
    AWS_COGNITO_CLIENT_ID: str = Field(..., env="AWS_COGNITO_CLIENT_ID")
    GH_API_TOKEN: str = Field(..., env="GH_API_TOKEN")
    GH_CLIENT_ID: str = Field(..., env="GH_CLIENT_ID")
    GH_CLIENT_SECRET: str = Field(..., env="GH_CLIENT_SECRET")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


creds = AWSCredentials()
cfg = Configuration()
