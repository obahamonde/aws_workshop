from aws_framework._cloudflare import CloudFlare
from aws_framework._config import cfg
from aws_framework._github import GithubClient
from aws_framework._types import *
from cd import app
from dockerclient import *

cf = CloudFlare()


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
    
@app.post("/api/github/template")
async def create_repo(repo: RepoTemplateCreate):
    print(repo.json())
    try:
        gh = GithubClient(repo.token)
        repo_response = await gh.create_repo_from_template(repo)
        container_create = ContainerCreate(
            login=repo.login,
            repo=repo.name,
            token=repo.token,
            email=repo.email,
            image=repo.template_repo
        )
        container_response = await get_pipeline(container_create)
        return {
            "repo": repo_response,
            "container": container_response,
        }
    except Exception as e:
        return {"error": str(e)}