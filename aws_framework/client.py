from typing import (Any, AsyncGenerator, Awaitable, Iterable, Iterator, Tuple,
                    cast)

import boto3
from aiohttp import ClientSession

from ._config import cfg, creds
from ._exceptions import AWSFrameworkException
from ._types import Json  # pylint: disable=no-name-in-module
from ._types import Headers, LazyProxy, Method, Optional
from .repository import *

MaybeHeaders = Optional[Headers]
MaybeJson = Optional[Json]
MaybeBytes = Optional[bytes]

class ApiClient(LazyProxy[ClientSession]):
    """

    Generic HTTP Client

    """

    def __load__(self) -> ClientSession:
        return ClientSession()

    async def fetch(
        self,
        url: str,
        method: Method = "GET",
        headers: MaybeHeaders = None,
        json: MaybeJson = None,
    ) -> MaybeJson:
        async with self.__load__() as session:
            async with session.request(
                method, url, headers=headers, json=json
            ) as response:
                try:
                    data = await response.json()
                    return data
                except (
                    AWSFrameworkException,
                    ValueError,
                    KeyError,
                    TypeError,
                    Exception,
                ) as exc:
                    print(exc)
                    return None

    async def text(
        self,
        url: str,
        method: Method = "GET",
        headers: MaybeHeaders = None,
        json: MaybeJson = None,
    ) -> Optional[str]:
        async with self.__load__() as session:
            async with session.request(
                method, url, headers=headers, json=json
            ) as response:
                try:
                    data = await response.text()
                    return data
                except (
                    AWSFrameworkException,
                    ValueError,
                    KeyError,
                    TypeError,
                    Exception,
                ) as exc:
                    print(exc)
                    return None

    async def stream(
        self,
        url: str,
        method: Method = "GET",
        headers: MaybeHeaders = None,
        json: MaybeJson = None,
    ) -> AsyncGenerator[str, None]:
        async with self.__load__() as session:
            async with session.request(
                method, url, headers=headers, json=json
            ) as response:
                async for chunk in response.content.iter_chunked(1024):
                    yield chunk.decode()

    async def blob(
        self,
        url: str,
        method: Method = "GET",
        headers: MaybeHeaders = None,
        json: MaybeJson = None,
    ) -> MaybeBytes:
        async with self.__load__() as session:
            async with session.request(
                method, url, headers=headers, json=json
            ) as response:
                try:
                    data = await response.read()
                    return data
                except (
                    AWSFrameworkException,
                    ValueError,
                    KeyError,
                    TypeError,
                    Exception,
                ) as exc:
                    print(exc)
                    return None
                
class ServerlessApi(LazyProxy[boto3.Session]):
    executor = ThreadPoolExecutor(max_workers=5)

    def __load__(self) -> boto3.Session:
        try:
            return boto3.Session(
                aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY,
                region_name=creds.AWS_DEFAULT_REGION,
            )
        except Exception as exc:
            print(exc)
            raise AWSFrameworkException("Failed to load AWS Session")

    @property
    def ecr(self):
        return self.__load__().client("ecr")
    
    def __call__(self) -> Any:
        return self.__load__().client("lambda")
       
    @asyncify
    def upsert_lambda(
        self, name: str, image: str, role: str = cfg.AWS_LAMBDA_ROLE, timeout: int = 300
    ) -> Awaitable[Json]:
        try:
            return self.__call__().update_function_code(
                FunctionName=name,
                ImageUri=image,
                Publish=True,
            )
        except Exception as exc:
            print(exc)
            response = self.__call__().create_function(
                FunctionName=name,
                Role=role,
                Code={"ImageUri": image},
                Timeout=timeout,
                Publish=True,
                Region="us-east-1",
            )
            self.__call__().add_permission(
                FunctionName=response["FunctionName"],
                StatementId=name,
                Action="lambda:InvokeFunctionUrl",
                Principal="*",
                FunctionUrlAuthType="NONE",
            )
            lambda_url = self.__call__().create_function_url_config(
                FunctionName=response["FunctionName"], AuthType="NONE"
            )
            url = lambda_url["Url"]
            return url
