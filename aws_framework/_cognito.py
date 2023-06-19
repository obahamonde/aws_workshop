from boto3 import Session

from ._config import cfg, creds
from ._decorators import asyncify
from ._types import *
from .utils import aws_parse


class CognitoClient:
    executor = ThreadPoolExecutor(max_workers=10)

    @property
    def client(self):
        return Session(**creds.dict()).client("cognito-idp")

    @asyncify
    def signup_endpoint(
        self, username: str, password: str, email: str, name: str, picture: str
    ) -> Awaitable[None]:
        return self.client.sign_up(
            ClientId=cfg.AWS_COGNITO_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "name", "Value": name},
                {"Name": "picture", "Value": picture},
            ],
        )

    @asyncify
    def confirm_signup(self, username: str, code: str) -> Awaitable[Any]:
        return self.client.confirm_sign_up(
            ClientId=cfg.AWS_COGNITO_CLIENT_ID, Username=username, ConfirmationCode=code
        )

    @asyncify
    def login_endpoint(self, username: str, password: str) -> Awaitable[Any]:
        return self.client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
            ClientId=cfg.AWS_COGNITO_CLIENT_ID,
        )

    @asyncify
    def get_user(self, access_token: str) -> Awaitable[Any]:
        response = self.client.get_user(AccessToken=access_token)
        return cast(Awaitable[Any], aws_parse(response["UserAttributes"]))

    @asyncify
    def forgot_password(self, username: str) -> Awaitable[Any]:
        return self.client.forgot_password(
            ClientId=cfg.AWS_COGNITO_CLIENT_ID, Username=username
        )

    @asyncify
    def confirm_forgot_password(
        self, username: str, code: str, password: str
    ) -> Awaitable[Any]:
        return self.client.confirm_forgot_password(
            ClientId=cfg.AWS_COGNITO_CLIENT_ID,
            Username=username,
            ConfirmationCode=code,
            Password=password,
        )
