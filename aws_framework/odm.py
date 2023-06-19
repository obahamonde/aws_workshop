from __future__ import annotations

from .repository import *
from .utils import gen_port


class NoSQLModel(DynaModel):
    """DynamoDB ODM"""

    @classmethod
    def db(cls: Type[D]) -> Repository[D]:
        """Gets the repository instance."""
        return Repository[cls]()

    @classmethod
    def __class_getitem__(cls, item: Type[D]) -> Type[D]:
        """Gets the repository instance."""
        return item

    @classmethod
    async def get(cls: Type[D], pk: str, sk: str) -> D:
        """Gets an item from a DynamoDB table."""
        return await cls.db().get(klass=cls, pk=pk, sk=sk)  # type: ignore

    @classmethod
    async def scan(cls: Type[D]) -> List[D]:
        """Scans a DynamoDB table."""
        return await cls.db().scan(klass=cls)  # type: ignore

    @classmethod
    async def put(cls: Type[D], instance: D) -> bool:
        """Puts an item into a DynamoDB table."""
        response = await cls.db().put(instance=instance)  # type: ignore
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return True
        return False

    @classmethod
    async def delete(cls, pk: str, sk: str) -> Dict[str, Any]:
        """Deletes an item from a DynamoDB table."""
        return await cls.db().delete(klass=cls, pk=pk, sk=sk)

    @classmethod
    async def update(cls: Type[D], pk: str, sk: str, update: Dict[str, Any]) -> D:
        """Updates an item in a DynamoDB table."""
        return await cls.db().update(klass=cls, pk=pk, sk=sk, update=update)  # type: ignore

    async def save(self: D) -> D:
        """Saves an item into a DynamoDB table."""
        try:
            return await self.get(self.dict()[self.pk()], self.dict()[self.sk()])  # type: ignore
        except:
            await self.put(self)
            return await self.get(self.dict()[self.pk()], self.dict()[self.sk()])  # type: ignore

    @classmethod
    async def drop_table(cls) -> Dict[str, Any]:
        """Drops a DynamoDB table."""
        return await cls.db().drop_table(klass=cls)

    @classmethod
    async def create_table(cls) -> Dict[str, Any]:
        """Creates a DynamoDB table."""
        return await cls.db().create_table(table_input=await cls._table_input())

    @classmethod
    async def _table_input(cls) -> CreateTableInput:
        """Converts a Pydantic model to a DynamoDB table input."""
        return await cls.db().table_input(klass=cls)

    @classmethod
    async def list_tables(cls) -> Dict[str, Any]:
        """Lists all DynamoDB tables."""
        return await cls.db().list_tables()

    @classmethod
    async def describe_table(cls) -> Dict[str, Any]:
        """Describes a DynamoDB table."""
        return await cls.db().describe_table(klass=cls)
