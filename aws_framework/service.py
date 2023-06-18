from asyncio import Condition
from re import I
from typing import *

import boto3
from boto3.dynamodb.conditions import ConditionExpressionBuilder
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from ._config import AWSCredentials, creds
from ._decorators import asyncify
from ._types import *
from .data import DynaModel, Field

D = TypeVar("D", bound=DynaModel)


class Partial(Generic[D]):
    """A factory class for creating partial versions of BaseModel subclasses."""

    def __class_getitem__(cls, model: Type[D]) -> Type[D]:
        return cls.create_partial(model)

    @staticmethod
    def create_partial(model: Type[D]) -> Type[D]:
        """Create a partial version of a BaseModel subclass."""
        return create_model(
            f"Partial{model.__name__}",
            **{name: (Optional[type_], None) for name, type_ in model.__annotations__.items()},  # type: ignore
            __base__=model,
        )


class Serializer(Generic[D]):
    """Serializer class that will take a Pydantic model
    and will convert it to a DynamoDB item and vice versa."""

    serializer: TypeSerializer = TypeSerializer()
    deserializer: TypeDeserializer = TypeDeserializer()
    executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)

    @asyncify
    def serialize(self, instance: M) -> Awaitable[Dict[str, Any]]:
        """Converts a Pydantic model to a DynamoDB item."""
        return self.serializer.serialize(instance.dict())["M"]

    @asyncify
    def deserialize(self, dct: dict[str, Any]) -> Awaitable[M]:
        """Converts a DynamoDB item to a Pydantic model."""
        return self.deserializer.deserialize({"M": dct})

    @asyncify
    def table_input(self, instance: M) -> Awaitable[CreateTableInput]:
        """Converts a Pydantic model to a DynamoDB table input."""

        key_schema = []
        attributes_definitions = []
        for k, v in instance.__fields__.items():
            if v.field_info.extra.get("index") in ("pk", "sk"):
                if v.field_info.extra.get("index") == "pk":
                    key_schema.append(KeySchemaElement(AttributeName=k, KeyType="HASH"))
                elif v.field_info.extra.get("index") == "sk":
                    key_schema.append(
                        KeySchemaElement(AttributeName=k, KeyType="RANGE")
                    )
                _type = v.type_
                if _type in (
                    str,
                    HttpUrl,  # pylint: disable=undefined-variable
                    IPvAnyAddress,  # pylint: disable=undefined-variable
                    IPvAnyInterface,  # pylint: disable=undefined-variable
                    IPvAnyNetwork,  # pylint: disable=undefined-variable
                    UUID,
                    datetime,
                    Method,
                    Index,
                ):
                    _type = "S"
                elif _type in (int, float, Decimal):
                    _type = "N"
                elif _type in (bytes, Binary, bytearray, memoryview):
                    _type = "B"
                else:
                    raise TypeError(f"Type {_type} not supported")
                attributes_definitions.append(
                    AttributeDefinition(AttributeName=k, AttributeType=_type)
                )
        table_input = CreateTableInput(
            TableName=instance.__name__,  # type: ignore
            AttributeDefinitions=attributes_definitions,
            KeySchema=key_schema,
            BillingMode="PAY_PER_REQUEST",
        )
        return cast(Awaitable[CreateTableInput], table_input)


class Service(Generic[D]):
    """DynamoDB Cloud API service class."""

    client = boto3.client("dynamodb", **creds.dict())
    resource = boto3.resource("dynamodb", **creds.dict())
    creds: AWSCredentials = creds
    executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)
    serializer: Serializer[D] = Serializer[D]()
    builder: ConditionExpressionBuilder = ConditionExpressionBuilder()

   

    async def table_input(self, class_name: Type[D]) -> CreateTableInput:
        """Converts a Pydantic model to a DynamoDB table input."""
        return await self.serializer.table_input(class_name)

    def serialize(self, instance: D) -> Awaitable[Dict[str, Any]]:
        """Converts a Pydantic model to a DynamoDB item."""
        return self.serializer.serialize(instance)

    def deserialize(self, dct: dict[str, Any]) -> Awaitable[D]:
        """Converts a DynamoDB item to a Pydantic model."""
        return self.serializer.deserialize(dct)

    @asyncify
    def create_table(self, table_input: CreateTableInput) -> Awaitable[Dict[str, Any]]:
        """Creates a DynamoDB table."""
        return self.client.create_table(**table_input.dict())

    @asyncify
    def put(self, name: str, serialized: Dict[str, Any]) -> Awaitable[Dict[str, Any]]:
        """Puts an item into a DynamoDB table."""
        return self.client.put_item(
            TableName=name,
            Item=serialized,
        )

    @asyncify
    def get(
        self, klass: Type[DynaModel], pk: str, sk: str
    ) -> Awaitable[Dict[str, Any]]:
        """Gets an item from a DynamoDB table."""
        return self.client.get_item(
            Key={klass.pk(): {"S": pk}, klass.sk(): {"S": sk}}, TableName=klass.__name__
        )

    @asyncify
    def delete(
        self,
        klass: Type[DynaModel],
        pk: str,
        sk: str,
    ) -> Awaitable[Dict[str, Any]]:
        """Deletes an item from a DynamoDB table."""
        return self.client.delete_item(
            Key={klass.pk(): {"S": pk}, klass.sk(): {"S": sk}}, TableName=klass.__name__
        )

    @asyncify
    def update(
        self, klass: Type[DynaModel], pk: str, sk: str, update: Dict[str, Any]
    ) -> Awaitable[Dict[str, Any]]:
        """Updates an item in a DynamoDB table."""
        return self.client.update_item(
            Key={klass.pk(): {"S": pk}, klass.sk(): {"S": sk}},
            TableName=klass.__name__,
            UpdateExpression=update,
        )

    @asyncify
    def scan(
        self, klass: Type[DynaModel], limit: int = 100
    ) -> Awaitable[Dict[str, Any]]:
        """Scans a DynamoDB table."""
        return self.client.scan(TableName=klass.__name__, Limit=limit)

    @asyncify
    def drop_table(self, klass: Type[DynaModel]) -> Awaitable[Dict[str, Any]]:
        """Deletes a DynamoDB table."""
        return self.client.delete_table(TableName=klass.__name__)

    @asyncify
    def list_tables(self) -> Awaitable[Dict[str, Any]]:
        """Lists DynamoDB tables."""
        return self.client.list_tables()

    @asyncify
    def describe_table(self, klass: Type[DynaModel]) -> Awaitable[Dict[str, Any]]:
        """Describes a DynamoDB table."""
        return self.client.describe_table(TableName=klass.__name__)

