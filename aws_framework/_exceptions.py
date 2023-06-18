from typing import Literal

from aiohttp.web_exceptions import HTTPException
from boto3.exceptions import Boto3Error
from botocore.exceptions import ClientError

Status = Literal["success", "info", "warning", "error"]


def status_type(value: int) -> Status:
    """Return the status type of a status code"""
    if value < 300:
        return "success"
    if value < 400:
        return "info"
    if value < 500:
        return "warning"
    return "error"


class AWSFrameworkException(Boto3Error, ClientError, HTTPException, Exception):
    """Base exception for all exceptions raised by this framework"""

    def __init__(self, message: str, status_code: int = 500):
        self.status_code = status_code
        self.message = message

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} {self.status_code}: {self.message}>"

    def __repr__(self) -> str:
        return str(self)

    def json(self) -> dict[str, str]:
        """Return a JSON representation of the exception"""
        return {
            "message": self.message,
            "status": status_type(self.status_code),
        }
