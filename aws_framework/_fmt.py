import asyncio
import base64
import json
import uuid
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import date, datetime, timezone
from enum import Enum
from json import JSONEncoder, dumps, loads
from time import time
from typing import Any, List
from uuid import UUID

from aiohttp.web import Request
from boto3.dynamodb.types import Binary, Decimal
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from typing_extensions import override

from ._exceptions import AWSFrameworkException


def datetime_string(dtime: datetime) -> str:
    """Return a human readable string representing 'time' weither in the past or in the future"""

    now = datetime.now().replace(tzinfo=timezone.utc)
    delta = relativedelta(now, dtime) if now > dtime else relativedelta(dtime, now)

    time_units = ["years", "months", "days", "hours", "minutes", "seconds"]

    for unit in time_units:
        value = getattr(delta, unit)
        if value != 0:
            ago_or_in = "ago" if now > dtime else "in"
            time_str = f"{abs(value)} {unit[:-1] if abs(value) == 1 else unit}"
            break
    else:
        time_str, ago_or_in = "Just now", ""

    return f"{dtime.strftime('%A %d %B %Y @%I:%M:%S %p')} ({time_str} {ago_or_in})"


def parse_json(json_string):
    try:
        return loads(json_string, parse_obj_hook=hook)
    except ValueError:
        pass


def hook(dct):
    if "@date" in dct:
        return datetime.strptime(dct["@date"], "%Y-%m-%dT%H:%M:%S.%f")
    if "@bytes" in dct:
        return urlsafe_b64decode(dct["@bytes"].encode("utf-8"))
    return dct


def to_json(dct, pretty=True, sort_keys=True):
    if pretty:
        return dumps(
            dct,
            cls=SwaggerEncoder,
            sort_keys=True,
            indent=4,
            separators=(", ", ": "),
            allow_nan=False,
            ensure_ascii=True,
        )
    return dumps(
        dct,
        cls=SwaggerEncoder,
        sort_keys=sort_keys,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=True,
    )


class SwaggerEncoder(JSONEncoder):
    @override
    def default(self, obj):
        if isinstance(obj, datetime):
            return datetime_string(obj)
        if isinstance(obj, date):
            return {"@date": obj.isoformat()}
        if isinstance(obj, (bytes, bytearray)):
            return {"@bytes": urlsafe_b64encode(obj).decode("utf-8")}
        if isinstance(obj, BaseModel):
            return obj.dict()
        if isinstance(obj, Request):
            if obj.content_type in (
                "application/json",
                "application/x-www-form-urlencoded",
            ):
                data = parse_json(obj.content.read_nowait().decode())
                if data:
                    return {
                        "method": obj.method,
                        "path": obj.path,
                        "headers": dict(obj.headers),
                        "body": data,
                    }
            elif obj.content_type == "multipart/form-data":
                data = {}
                for k, v in asyncio.run(obj.post()):
                    _v = None
                    try:
                        _v = loads(v)
                    except ValueError:
                        _v = "file"
                    data[k] = v
            else:
                data = None
                return {
                    "method": obj.method,
                    "query_params": dict(obj.query),
                    "path_params": dict(obj.match_info),
                    "headers": dict(obj.headers),
                    "body": data,
                }


def jsonable_encoder(
    obj: Any,
    *,
    include: List[str] = [],
    exclude: List[str] = [],
    by_alias: bool = False,
    skip_defaults: bool = False,
    custom_encoder: Any = None,
) -> Any:
    """
    Convert any object to a JSON-serializable object.

    This function is used by Aiofauna to convert objects to JSON-serializable objects.

    It supports all the types supported by the standard json library, plus:

    * datetime.datetime
    * datetime.date
    * datetime.time
    * uuid.UUID
    * enum.Enum
    * pydantic.BaseModel
    """

    if custom_encoder is None:
        custom_encoder = SwaggerEncoder

    if obj is str:
        return "string"
    if obj is int or obj is float:
        return "integer"
    if obj is bool:
        return "boolean"
    if obj is None:
        return "null"
    if obj is list:
        return "array"
    if obj is dict:
        return "object"
    if obj is bytes:
        return "binary"
    if obj is datetime:
        return "date-time"
    if obj is date:
        return "date"
    if obj is time:
        return "time"
    if obj is UUID:
        return "uuid"
    if obj is Enum:
        return "enum"
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, (list, tuple, set, frozenset)):
        return [
            jsonable_encoder(
                v,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                custom_encoder=custom_encoder,
            )
            for v in obj
        ]
    if isinstance(obj, dict):
        return {
            jsonable_encoder(
                k,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                custom_encoder=custom_encoder,
            ): jsonable_encoder(
                v,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                custom_encoder=custom_encoder,
            )
            for k, v in obj.items()
        }
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode()
    if isinstance(obj, (set, frozenset)):
        return [
            jsonable_encoder(
                v,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                custom_encoder=custom_encoder,
            )
            for v in obj
        ]
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, UUID):
        return str(obj)
    return custom_encoder().default(obj)


class AWSEncoder(json.JSONEncoder):

    """JSON encoder for AWS objects"""

    def default(self, o) -> Any:
        """Default encoder"""
        if isinstance(o, datetime):
            return datetime_string(o)
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, Binary):
            return base64.b64encode(o.value).decode("utf-8")
        if isinstance(o, dict):
            return {k: self.default(v) for k, v in o.items()}
        if isinstance(o, list):
            return [self.default(e) for e in o]
        if isinstance(o, BaseModel):
            return o.dict()
        if isinstance(o, AWSFrameworkException):
            return o.json()
        return super().default(o)
