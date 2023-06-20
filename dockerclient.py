from typing import *

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from aws_framework._types import *
from aws_framework.client import ApiClient, MaybeBytes
from aws_framework.odm import Field, NoSQLModel
from aws_framework.utils import gen_port


class ContainerCreate(BaseModel):
    """
    - ContainerCreate
        - login:str
        - repo:str
        - token:str
        - email:str
        - image:str = "codeserver"
    """

    login: str = Field(..., description="User reference")
    repo: str = Field(..., description="Repo reference")
    token: str = Field(..., description="Github token")
    email: str = Field(..., description="Email of the user")
    image: str = Field(..., description="Image to use")


class CodeServer(NoSQLModel):
    """
    - CodeServer
        - login:str
        - repo:str
        - container_id:str
        - image:str
        - host_port:int
        - env_vars:List[str]

        - payload(token:str, volume:str) -> Dict[str, Any]
    """

    login: str = Field(..., index="pk")
    repo: str = Field(..., description="User reference", index="sk")
    container_id: Optional[str] = Field(default=None)
    image: str = Field(default="codeserver", description="Image to use")
    host_port: int = Field(default_factory=gen_port, description="Port to expose")
    email: str = Field(..., description="Email of the user")
    env_vars: Optional[List[str]] = Field(
        default=[], description="Environment variables"
    )

    def payload(self, token: str, volume: str) -> JSON:
        extensions = [
            "ms-python.isort",
            "ms-python.python",
            "TabNine.tabnine-vscode",
            "PKief.material-icon-theme",
            "esbenp.prettier-vscode",
            "ms-python.isort",
            "ms-pyright.pyright",
            "RobbOwen.synthwave-vscode",
        ]
        assert isinstance(self.env_vars, list)
        self.env_vars.append(f"GH_TOKEN={token}")
        self.env_vars.append(f"GH_REPO=https://github.com/{self.login}/{self.repo}")
        self.env_vars.append(f"EMAIL={self.email}")
        self.env_vars.append(f"PASSWORD={self.login}")
        self.env_vars.append("TZ=America/New_York")
        self.env_vars.append(f"PUID={self.login}")
        self.env_vars.append(f"PGID={self.login}")
        self.env_vars.append(f"USER={self.login}")
        self.env_vars.append(f"SUDO_PASSWORD={self.login}")
        git_startup_script = f"""
        git clone https://github.com/{self.login}/{self.repo} /{volume}:/config/workspace
        git config --global user.name {self.login}
        git config --global user.email {self.login}@github.com
        git config --global credential.helper 'store --file=/tmp/git_credentials'
        echo https://github.com/{self.login}:{token} > /tmp/git_credentials
        chmod 777 ./*
        chmod 777 ./**/*
        chmod 777 ./**/**/*
        code-server --install-extension {','.join(extensions)}
        code-server --auth {self.login} --bind-addr 0.0.0.0:{self.host_port} --disable-telemetry --disable-update-check
        """
        self.env_vars.append(f"STARTUP_SCRIPT={git_startup_script}")
        return {
            "Image": self.image,
            "Env": self.env_vars,
            "ExposedPorts": {"8443/tcp": {"HostPort": str(self.host_port)}},
            "HostConfig": {
                "PortBindings": {"8443/tcp": [{"HostPort": str(self.host_port)}]},
                "Binds": [f"{volume}:/config/workspace"],
            },
        }


class Container(NoSQLModel):  # pylint: disable=class-already-defined
    """
    - Container
        - login:str
        - repo:str
        - container_id:str
        - image:str
        - host_port:int
        - env_vars:List[str]

        - payload(token:str, volume:str) -> Json
    """

    login: Optional[str] = Field(default=None, index="pk")
    repo: str = Field(..., description="Github Repo", index="sk")
    image: str = Field(..., description="Image to use")
    host_port: int = Field(default_factory=gen_port, description="Port to expose")
    container_port: int = Field(default=8080, description="Port to expose")
    env_vars: List[str] = Field(
        default=["DOCKER=1"], description="Environment variables"
    )
    container_id: Optional[str] = Field(default=None)

    def payload(self, token: str, volume: str) -> MaybeJson:
        assert isinstance(self.env_vars, list)
        self.env_vars.append(f"GH_TOKEN={token}")
        self.env_vars.append(f"GH_REPO=https://github.com/{self.login}/{self.repo}]")
        return {
            "Image": self.image,
            "Env": self.env_vars,
            "ExposedPorts": {
                f"{self.container_port}/tcp": {"HostPort": str(self.host_port)}
            },
            "HostConfig": {
                "PortBindings": {
                    f"{self.container_port}/tcp": [{"HostPort": str(self.host_port)}]
                },
                "Binds": [f"{volume}:/app"],
            },
        }


class DockerService(ApiClient):
    """Docker REST API Client"""

    base_url: str = "http://localhost:9898"

    async def fetch(
        self,
        url: str,
        method: Method = "GET",
        headers: MaybeHeaders = None,
        json: MaybeJson = None,
    ) -> MaybeJson:
        """Fetch a URL
        - (url:str, method:Method="GET", headers:Optional[Json]=None, json:Optional[Json]=None) -> Json
        """
        return await super().fetch(
            self.base_url + url, method=method, headers=headers, json=json
        )

    async def text(
        self,
        url: str,
        method: Method = "GET",
        headers: MaybeHeaders = None,
        json: MaybeJson = None,
    ) -> MaybeText:
        """Fetch a URL
        - (url:str, method:Method="GET", headers:Optional[Json]=None, json:Optional[Json]=None) -> Optional[str]
        """
        return await super().text(
            self.base_url + url, method=method, headers=headers, json=json
        )

    async def stream(
        self,
        url: str,
        method: Method = "GET",
        headers: MaybeHeaders = None,
        json: MaybeJson = None,
    ) -> AsyncGenerator[str, None]:
        """Fetch a URL
        - (url:str, method:Method="GET", headers:Optional[Json]=None, json:Optional[Json]=None) -> AsyncGenerator[str, None]
        """
        async for chunk in super().stream(
            self.base_url + url, method=method, headers=headers, json=json
        ):
            yield chunk

    async def blob(
        self,
        url: str,
        method: Method = "GET",
        headers: MaybeHeaders = None,
        json: MaybeJson = None,
    ) -> MaybeBytes:
        """Fetch a URL
        - (url:str, method:Method="GET", headers:Optional[Json]=None, json:Optional[Json]=None) -> AsyncGenerator
        """
        return await super().blob(
            self.base_url + url, method=method, headers=headers, json=json
        )

    async def start_container(self, container_id: str) -> None:
        """
        Starts a container
        - (container_id:str) -> None
        """
        await self.text(f"/containers/{container_id}/start", method="POST")

    async def create_volume(self, tag: str) -> str:
        """Create a volume
        - (tag:str) -> str
        """
        payload = {"Name": tag, "Driver": "local"}
        await self.fetch(
            "/volumes/create",
            method="POST",
            headers={"Content-Type": "application/json"},
            json=payload,
        )
        return tag

    async def create_container(self, body: ContainerCreate, volume: str) -> Container:
        """Create a python container
        - (body:ContainerCreate) -> Container
        """
        container = Container(**body.dict())
        payload = container.payload(body.token, volume)
        response = await self.fetch(
            "/containers/create",
            method="POST",
            headers={"Content-Type": "application/json"},
            json=payload,
        )
        assert isinstance(response, dict)
        container.container_id = response["Id"]
        instance = await container.save()
        assert isinstance(instance, Container)
        assert isinstance(instance.container_id, str)
        await self.start_container(instance.container_id)
        return instance

    async def create_code_server(
        self, body: ContainerCreate, volume: str
    ) -> CodeServer:
        codeserver = CodeServer(**body.dict())
        payload = codeserver.payload(body.token, volume)
        response = await self.fetch(
            "/containers/create",
            method="POST",
            headers={"Content-Type": "application/json"},
            json=payload,
        )
        assert isinstance(response, dict)
        codeserver.container_id = response["Id"]
        instance = await codeserver.save()
        assert isinstance(instance, CodeServer)
        assert isinstance(instance.container_id, str)
        await self.start_container(instance.container_id)
        return instance
