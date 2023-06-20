# Controller code:

@app.post("/api/github/workspace")
async def get_pipeline(body: ContainerCreate):
    try:
        token = body.token
        docker = DockerService()
        volume = await docker.create_volume(tag=body.login)
        ide = ContainerCreate(
            login=body.login,
            repo=body.repo,
            token=token,
            email=body.email,
            image="codeserver"
        )
        _app = await docker.create_container(body, volume)
        codeserver = await docker.create_code_server(ide, volume)
        dns_app = await cf.provision(body.login, _app.host_port)
        dns_codeserver = await cf.provision(body.login+"-"+body.image, codeserver.host_port)
        preview = {
            "url": dns_app["url"],
            "ip": f"{cfg.IP_ADDR}:{_app.host_port}",
            "container": _app.container_id,
        }
        workspace = {
            "url": dns_codeserver["url"],
            "ip": f"{cfg.IP_ADDR}:{codeserver.host_port}",
            "container": codeserver.container_id,
        }
        return {
            "workspace": workspace,
            "preview": preview,
            "repo": body.repo,
        }
    except Exception as e:
        return {"error": str(e)}


# Service code:

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


# Model code:

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
        git clone https://github.com/{self.login}/{self.repo} /app
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