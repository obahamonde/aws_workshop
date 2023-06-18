from abc import abstractproperty

from boto3.session import Session
from pydantic import BaseModel as M
from pydantic import Field as field

from ._config import AWSCredentials, cfg, creds
from ._decorators import aio, asyncify
from ._types import *


class Resource(LazyProxy[Session], ABC):
    """Base class for AWS resources."""

    def __load__(self) -> Session:
        return Session(creds)

    @abstractmethod
    def request(self, action: str, params: dict[str, Any]) -> Any:
        ...


class BaseResource(Resource):
    schemain: Type[BaseModel]
    schemaout: Type[BaseModel]
    executor = ThreadPoolExecutor(max_workers=5)
    name: str

    def __init__(
        self, name: str, schemain: Type[BaseModel], schemaout: Type[BaseModel]
    ):
        self.name = name
        self.schemain = schemain
        self.schemaout = schemaout

    @asyncify
    def request(self, action: str, params: dict[str, Any]) -> Any:
        return getattr(self.client, action)(**params)

    @property
    def client(self) -> Any:
        return getattr(self.resource, self.name)

    @property
    def resource(self) -> Any:
        return self._load_().resource(self.name)

    def __load__(self) -> Session:
        return Session(creds)


class LambdaCreate(BaseModel):
    FunctionName: str = field(...)
    Runtime: str = field(default="python3.8")
    Role: str = field(default=cfg.AWS_LAMBDA_ROLE)
    Handler: str = field(default="main.handler")
    Code: dict[str, Any] = field(...)
    Description: Optional[str] = field(default=None)
    Timeout: int = field(default=3)
    MemorySize: int = field(default=128)
    Publish: bool = field(default=True)
    VpcConfig: Optional[dict[str, Any]] = field(default=None)
    PackageType: str = field(default="Zip")
    Tags: Optional[dict[str, Any]] = field(default=None)
    Layers: Optional[list[str]] = field(default=None)
    DeadLetterConfig: Optional[dict[str, Any]] = field(default=None)
    Environment: Optional[dict[str, Any]] = field(default=None)
    KMSKeyArn: Optional[str] = field(default=None)
    TracingConfig: Optional[dict[str, Any]] = field(default=None)
    RevisionId: Optional[str] = field(default=None)
    FileSystemConfigs: Optional[list[dict[str, Any]]] = field(default=None)
    ImageConfig: Optional[dict[str, Any]] = field(default=None)
    CodeSigningConfigArn: Optional[str] = field(default=None)
    Architectures: Optional[list[str]] = field(default=None)
    SigningProfileVersionArn: Optional[str] = field(default=None)
    SigningJobArn: Optional[str] = field(default=None)
    Tags: Optional[dict[str, Any]] = field(default=None)
