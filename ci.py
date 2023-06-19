from aws_framework._cloudflare import CloudFlare
from aws_framework._config import cfg
from aws_framework._github import GithubClient
from aws_framework._types import *
from cd import app
from dockerclient import *

cf = CloudFlare()


@app.post("/api/github/workspace")
async def get_pipeline(body: ContainerCreate):
    docker = DockerService()
    volume = await docker.create_volume(tag=body.login)
    python = await docker.create_container(body, volume)
    codeserver = await docker.create_code_server(body, volume)
    dns_python = await cf.provision(body.login+"py", python.host_port)
    dns_codeserver = await cf.provision(body.login, codeserver.host_port)
    return {
        "python": {
            "url": dns_python["url"],
            "ip": f"{cfg.IP_ADDR}:{python.host_port}",
            "container": python.container_id,
        },
        "codeserver": {
            "url": dns_codeserver["url"],
            "ip": f"{cfg.IP_ADDR}:{codeserver.host_port}",
            "container": codeserver.container_id,
        },
    }
    
@app.post("/api/github/repo")
async def create_repo(token: str, repo: CreateRepo):
    gh = GithubClient(token)
    return await gh.create_repo(repo)
