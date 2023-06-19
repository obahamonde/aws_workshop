import asyncio

from botocore.exceptions import ClientError

from ._exceptions import AWSFrameworkException
from .service import *


class Repository(Generic[D]):
    """Repository class that will take the service
    and will perform all operations with DynamoDB."""

    service: Service[D] = Service[D]()

    async def put(self, instance: D) -> Dict[str, Any]:
        """Puts an item into a DynamoDB table."""
        serialized = await self.service.serialize(instance)
        return await self.service.put(
            name=instance.__class__.__name__, serialized=serialized
        )

    async def scan(self, klass: Type[D]) -> List[D]:
        """Scans a DynamoDB table."""
        data = await self.service.scan(klass=klass)
        return await asyncio.gather(
            *[self.service.deserialize(item) for item in data["Items"]]
        )

    async def create_table(self, table_input: CreateTableInput) -> Dict[str, Any]:
        """Creates a DynamoDB table."""
        try:
            return await self.service.create_table(table_input)
        except ClientError as e:
            return AWSFrameworkException(e.response["Error"]["Message"]).json()

    async def get(self, klass: Type[D], pk: str, sk: str) -> D:
        """Gets an item from a DynamoDB table."""
        data = await self.service.get(klass=klass, pk=pk, sk=sk)
        response = await self.service.deserialize(data["Item"])
        print(response)
        print(type(response))
        return klass(**response)

    async def delete(self, klass: Type[D], pk: str, sk: str) -> Dict[str, Any]:
        """Deletes an item from a DynamoDB table."""
        return await self.service.delete(klass=klass, pk=pk, sk=sk)

    async def update(
        self, klass: Type[D], pk: str, sk: str, update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Updates an item in a DynamoDB table."""
        return await self.service.update(klass=klass, pk=pk, sk=sk, update=update)

    async def drop_table(self, klass: Type[DynaModel]) -> Dict[str, Any]:
        """Drops a DynamoDB table."""
        return await self.service.drop_table(klass=klass)

    async def table_input(self, klass: Type[D]) -> CreateTableInput:
        """Converts a Pydantic model to a DynamoDB table input."""
        return await self.service.table_input(klass)

    async def list_tables(self) -> Dict[str, Any]:
        """Lists all DynamoDB tables."""
        return await self.service.list_tables()

    async def describe_table(self, klass: Type[D]) -> Dict[str, Any]:
        """Describes a DynamoDB table."""
        return await self.service.describe_table(klass=klass)
