from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import *
from uuid import UUID

from boto3.dynamodb.types import Binary, Decimal, TypeDeserializer, TypeSerializer
from multidict import CIMultiDict, CIMultiDictProxy, MultiDict, MultiDictProxy
from pydantic import *
from pydantic import IPvAnyNetwork  # pylint: disable=no-name-in-module
from pydantic.fields import Field  # pylint: disable=no-name-in-module
from pydantic.main import *
from pydantic.main import BaseModel  # pylint: disable=no-name-in-module
from pydantic.main import create_model  # pylint: disable=no-name-in-module

from ._decorators import aio, asyncify

Method = Literal[
    "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE", "CONNECT"
]

Headers = Union[
    MultiDict[str],
    CIMultiDict[str],
    MultiDictProxy[str],
    CIMultiDictProxy[str],
    dict,
    Dict[str, str],
]

Index = Literal["pk", "sk", "gsi", "lsi"]

N = Union[int, float, Decimal]
M = Union[bytes, Binary, bytearray, memoryview]
S = Union[
    str,
    HttpUrl,  # pylint: disable=undefined-variable
    IPvAnyAddress,  # pylint: disable=undefined-variable
    IPvAnyInterface,  # pylint: disable=undefined-variable
    IPvAnyNetwork,
    UUID,
    datetime,
    Method,
    Index,
]
M = Union[dict, Dict[str, Any], BaseModel, Headers]
L = Union[list, List[Union[N, M, S, M, "L"]]]
NULL = Union[None, Literal["null", "Null"]]
BOOL = Union[bool, Literal["true", "false", "True", "False"]]
SS = List[S]
BS = List[M]
NS = List[N]

M = TypeVar("M", bound=BaseModel)

T = TypeVar("T")


class LazyProxy(Generic[T], ABC):
    """
    A LazyLoading proxy object that defers the loading of an object until it is accessed.
    It generates types dynamically, so it can be used as a base class for other classes.
    These classes will benefit from the lazy loading behavior which improves performance.
    Also, it can be used as a decorator for functions, which will be called when the function is called.
    Subclasses must implement the __load__ method to provide the logic for loading the proxied object.
    Usage:
    1. Subclass LazyProxy and implement the __load__ method.
    2. Accessing attributes, calling methods, or using other operations on the LazyProxy instance will trigger
         the loading of the proxied object.
    """

    def __init__(self) -> None:
        self.__proxied: T | None = None

    def __getattr__(self, attr: str) -> object:
        return getattr(self.__get_proxied__(), attr)

    def __repr__(self) -> str:
        return repr(self.__get_proxied__())

    def __dir__(self) -> Iterable[str]:
        return self.__get_proxied__().__dir__()

    def __get_proxied__(self) -> T:
        proxied = self.__proxied
        if proxied is not None:
            return proxied

        self.__proxied = proxied = self.__load__()
        return proxied

    def __set_proxied__(self, value: T) -> None:
        self.__proxied = value

    def __as_proxied__(self) -> T:
        """Helper method that returns the current proxy, typed as the loaded object"""
        return cast(T, self)

    @abstractmethod
    def __load__(self) -> T:
        ...


# Identity Objects


class AttributeDefinition(BaseModel):
    """Represents an attribute for describing the key schema for the table and indexes."""

    AttributeName: str = Field(..., max_length=255)
    AttributeType: str = Field(..., regex="^(S|N|B)$")


class KeySchemaElement(BaseModel):
    """Represents a single element of a key schema."""

    AttributeName: str = Field(..., max_length=255)
    KeyType: str = Field(..., regex="^(HASH|RANGE)$")


class CreateTableInput(BaseModel):
    """Represents the input of a CreateTable operation."""

    TableName: str = Field(..., max_length=255)
    AttributeDefinitions: List[AttributeDefinition]
    KeySchema: List[KeySchemaElement]
    BillingMode: str = Field("PAY_PER_REQUEST", const=True)

    class Config:
        extra = "forbid"
