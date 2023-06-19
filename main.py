from typing import *

from aiohttp.web import FileField, Request
from botocore import auth

from aws_framework import CognitoClient, Field, NoSQLModel, S3Client
from aws_framework._cloudflare import CloudFlare
from aws_framework._config import cfg
from aws_framework._github import GithubClient
from ci import app
from dockerclient import *


class User(NoSQLModel):
    sub: str = Field(None, description="The sub of the user", index="pk")
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email of the user", index="sk")
    picture: str = Field(..., description="The picture of the user")
    emailverified: bool = Field(
        False, description="The email verification status of the user"
    )

s3 = S3Client()

auth = CognitoClient()

cf = CloudFlare()

@app.post("/api/image")
async def upload_picture(request: Request) -> str:
    data = await request.post()
    picture = data["file"]
    assert isinstance(picture, FileField)
    await s3.put_object(
        cfg.AWS_S3_BUCKET, picture.filename, picture.file.read(), picture.content_type
    )
    return f"https://s3.amazonaws.com/{cfg.AWS_S3_BUCKET}/{picture.filename}"

@app.post("/api/signup")
async def signup(user: UserSignUp) -> str:
    return await auth.signup_endpoint(
        user.email, user.password, user.email, user.name, user.picture
    )

@app.post("/api/confirm")
async def confirm(username: str, code: str) -> str:
    return await auth.confirm_signup(username, code)

@app.post("/api/login")
async def login(user: UserLogin) -> AuthenticationResult:
    response = await auth.login_endpoint(user.username, user.password)
    return AuthenticationResult(**response["AuthenticationResult"])

@app.get("/api/user")
async def get_user(token: str):
    response = await auth.get_user(token)
    user = User(**dict(response))
    return await user.save()

@app.post("/api/forgot")
async def forgot_password(email: str):
    response = await auth.forgot_password(email)
    return response["CodeDeliveryDetails"]

@app.post("/api/confirm-forgot")
async def confirm_forgot_password(user: UserConfirmForgot):
    return await auth.confirm_forgot_password(user.username, user.code, user.password)

@app.get("/api/users")
async def get_users() -> List[User]:
    return await User.scan()

@app.post("/api/github")
async def callback(code: str):
    gh = GithubClient()
    gh.base_url = "https://github.com"
    payload = {
        "client_id": cfg.GH_CLIENT_ID,
        "client_secret": cfg.GH_CLIENT_SECRET,
        "redirect_uri": "http://localhost:3000",
        "code": code,
        "state": "1234",
    }
    response = await gh.post("/login/oauth/access_token", json=payload)
    assert isinstance(response, dict)
    access_token = response["access_token"]
    gh.base_url = "https://api.github.com"
    gh.headers.update({"Authorization": f"token {access_token}"})
    gh_user = await gh.get("/user")
    assert isinstance(gh_user, dict)
    user = User(
        **{
            "sub": gh_user["id"],
            "name": gh_user["login"],
            "email": gh_user["email"],
            "picture": gh_user["avatar_url"],
            "emailverified": gh_user["email"] is not None,
        }
    )
    return {"user": await user.save(), "token": access_token}

@app.get("/api/github/repos")
async def search_own_repos(token: str, query: str, login: str):
    gh = GithubClient(token)
    return await gh.search_repos(query, login)


def main():
    app.run()