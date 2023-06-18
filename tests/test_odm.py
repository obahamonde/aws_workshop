import asyncio
from datetime import datetime
from uuid import uuid4

import pytest

from aws_framework import Field, NoSQLModel
from aws_framework.repository import Repository


class MockDynaModel(NoSQLModel):
    """Mock DynaModel."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: str = Field(default_factory=datetime.now().isoformat)
    name: str = Field(..., index="pk")
    age: int = Field(..., index="sk")
    is_active: bool = Field(default=True)


@pytest.fixture(scope="module")
def model():
    yield MockDynaModel


@pytest.mark.asyncio
async def test_create_table(model):
    """Test the initiation and completion of the create table operation"""
    response = await model.create_table()
    assert response["TableDescription"]["TableName"] == model.__name__
    assert response["TableDescription"]["TableStatus"] == "CREATING"


@pytest.mark.asyncio
async def test_list_tables(model):
    """Test the table is created"""
    response = await model.list_tables()
    assert model.__name__ in response["TableNames"]
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


@pytest.mark.asyncio
async def test_describe_table(model):
    """Test the table is created"""
    await asyncio.sleep(10)
    response = await model.describe_table()
    assert response["Table"]["TableName"] == model.__name__
    assert response["Table"]["TableStatus"] == "ACTIVE"


@pytest.mark.asyncio
async def test_put(model):
    """Test the table is created"""
    mock = model(name="test", age=1)
    response = await mock.put(mock)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


@pytest.mark.asyncio
async def test_get(model):
    """Test the item can be retrieved"""
    response = await model.get(pk="test", sk="1")
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


@pytest.mark.asyncio
async def test_drop_table():
    """Test the table is created"""
    response = await model.drop_table(MockDynaModel.__name__)
    assert response["TableDescription"]["TableName"] == MockDynaModel.__name__
    assert response["TableDescription"]["TableStatus"] == "DELETING"
