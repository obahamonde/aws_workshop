from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import (
    Any,
    Generator,
    Generic,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
)

from boto3.dynamodb.conditions import (
    Attr,
    ConditionBase,
    ConditionExpressionBuilder,
    Key,
)
from boto3.dynamodb.types import Binary, Decimal, TypeDeserializer, TypeSerializer
from botocore.serialize import Serializer
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from pydantic import BaseConfig
from pydantic import Field as Pydantic  # pylint: disable=no-name-in-module
from pydantic.fields import ModelField  # pylint: disable=no-name-in-module
from pydantic.main import ModelMetaclass  # pylint: disable=no-name-in-module

from ._config import AWSCredentials, creds
from ._decorators import aio, asyncify
from ._fmt import AWSEncoder
from ._types import *


def Field(*args, index: Optional[Index] = None, **kwargs):  # pylint: disable=all
    """Value Object factory"""
    return Pydantic(*args, index=index, **kwargs)


class DynaModel(BaseModel):
    """Base class for DynamoDB models."""

    @classmethod
    def pk(cls) -> str:
        """Partition key"""
        for field in cls.__fields__.values():
            if field.field_info.extra.get("index") == "pk":
                return field.name
        return cls.__name__

    @classmethod
    def sk(cls) -> str:
        """Sort key"""
        for field in cls.__fields__.values():
            if field.field_info.extra.get("index") == "sk":
                return field.name
        return cls.__name__

    @classmethod
    def key_schema(cls) -> List[KeySchemaElement]:
        """Key schema"""
        return [
            KeySchemaElement(
                AttributeName=cls.pk(),
                KeyType="HASH",
            ),
            KeySchemaElement(
                AttributeName=cls.sk(),
                KeyType="RANGE",
            ),
        ]

    @classmethod
    def attribute_definitions(cls) -> List[AttributeDefinition]:
        """Attribute definitions"""
        return [
            AttributeDefinition(
                AttributeName=cls.pk(),
                AttributeType="S",
            ),
            AttributeDefinition(
                AttributeName=cls.sk(),
                AttributeType="S",
            ),
        ]

    def json(self, *args, **kwargs) -> str:
        """Serializes the model to a JSON string."""
        return super().json(*args, **kwargs, cls=AWSEncoder, exclude_none=True)

    def dict(self, *args, **kwargs) -> dict[str, Any]:
        """Serializes the model to a dictionary."""
        return super().dict(*args, **kwargs, exclude_none=True)


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
