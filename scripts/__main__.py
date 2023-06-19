import base64
import json
import os

import boto3
import click
import docker as dockerlib
from docker.models.images import Image
from dotenv import load_dotenv

load_dotenv()


class Client:
    @property
    def docker(self):
        return dockerlib.from_env()

    @property
    def ecr(self):
        return boto3.client("ecr")

    @property
    def apprunner(self):
        return boto3.client("apprunner")

    def __call__(self):
        return self.docker, self.ecr, self.apprunner


client = Client()
docker, ecr, apprunner = client()


def login():
    token = ecr.get_authorization_token()
    assert isinstance(token, dict)
    username, password = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
        .decode()
        .split(":")
    )
    registry = token["authorizationData"][0]["proxyEndpoint"]
    registry = registry.replace("https://", "")
    docker = client.docker
    docker.login(username, password, registry=registry)
    return docker, registry


def create_connection(repo: str):
    apprunner = boto3.client("apprunner")
    response = apprunner.create_connection(
        ConnectionName=repo,
        ProviderType="ECS",
        Tags=[
            {"Key": "Name", "Value": repo},
        ],
    )
    print(response)


@click.group()
def cli():
    """A tool for building and deploying containerized applications"""
    pass


@click.argument(
    "framework",
    type=click.Choice(["flask", "fastapi", "express", "codeserver"]),
    default="flask",
    required=False,
    nargs=1,
)
@cli.command()
def build(framework):
    """Creates a new project"""
    docker, ecr, apprunner = client()
    print(f"Building {framework} project")
    path = os.path.join(os.getcwd(), "scripts", "containers", framework)
    os.chdir(path)
    pack = docker.images.build(path=".", tag=f"app-{framework}")
    assert isinstance(pack, tuple)
    m, logs = pack
    print(logs)
    print(m)
    print(f"Pushing {framework} project")
    docker, registry = login()
    image = docker.images.get(f"app-{framework}")
    assert isinstance(image, Image)
    image.tag(f"{registry}/app-{framework}")
    docker.images.push(f"{registry}/app-{framework}")
    print(f"Pushed {framework} project")
    os.chdir(os.path.join(os.getcwd(), "..", "..", ".."))
    print(os.getcwd())
    print("Done")


@cli.command()
def list():
    """Lists all projects"""
    docker, registry = login()
    images = docker.images.list()
    for image in images:
        assert isinstance(image, Image)
        print(image.tags)


@cli.command()
def prune():
    """Deletes all projects"""
    docker, ecr, apprunner = client()
    images = docker.images.list()
    for image in images:
        assert isinstance(image, Image)
        docker.images.remove(image.id, force=True)
    repos = ecr.describe_repositories()
    for repo in repos["repositories"]:
        ecr.delete_repository(repositoryName=repo["repositoryName"], force=True)
    print("Done")


@cli.command()
def deploy():
    """Deploys all projects"""
    docker, ecr, apprunner = client()
    images = docker.images.list()
    for image in images:
        assert isinstance(image, Image)
        docker.images.push(image.tags[0])
    repos = ecr.describe_repositories()
    for repo in repos["repositories"]:
        ecr.delete_repository(repositoryName=repo["repositoryName"], force=True)
    print("Done")


if __name__ == "__main__":
    cli()
