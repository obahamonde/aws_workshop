from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import *
from uuid import UUID

from boto3.dynamodb.types import (Binary, Decimal, TypeDeserializer,
                                  TypeSerializer)
from multidict import CIMultiDict, CIMultiDictProxy, MultiDict, MultiDictProxy
from pydantic import *
from pydantic import IPvAnyNetwork  # pylint: disable=no-name-in-module
from pydantic.fields import Field  # pylint: disable=no-name-in-module
from pydantic.main import *
from pydantic.main import BaseModel  # pylint: disable=no-name-in-module
from pydantic.main import create_model  # pylint: disable=no-name-in-module

from ._decorators import aio, asyncify

Method = Literal[
    "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE", "CONNECT"
]

DefaultImages = Literal["flask-app", "express-app", "fastapi-app"]

Headers = Union[
    MultiDict[str],
    CIMultiDict[str],
    MultiDictProxy[str],
    CIMultiDictProxy[str],
    dict,
    Dict[str, str],
]

Index = Literal["pk", "sk", "gsi", "lsi"]

N = Union[int, float, Decimal]
M = Union[bytes, Binary, bytearray, memoryview]
S = Union[
    str,
    HttpUrl,  # pylint: disable=undefined-variable
    IPvAnyAddress,  # pylint: disable=undefined-variable
    IPvAnyInterface,  # pylint: disable=undefined-variable
    IPvAnyNetwork,
    UUID,
    datetime,
    Method,
    Index,
]
M = Union[dict, Dict[str, Any], BaseModel, Headers]
L = Union[list, List[Union[N, M, S, M, "L"]]]
NULL = Union[None, Literal["null", "Null"]]
BOOL = Union[bool, Literal["true", "false", "True", "False"]]
SS = List[S]
BS = List[M]
NS = List[N]

M = TypeVar("M", bound=BaseModel)

T = TypeVar("T")


class LazyProxy(Generic[T], ABC):
    """
    A LazyLoading proxy object that defers the loading of an object until it is accessed.
    It generates types dynamically, so it can be used as a base class for other classes.
    These classes will benefit from the lazy loading behavior which improves performance.
    Also, it can be used as a decorator for functions, which will be called when the function is called.
    Subclasses must implement the __load__ method to provide the logic for loading the proxied object.
    Usage:
    1. Subclass LazyProxy and implement the __load__ method.
    2. Accessing attributes, calling methods, or using other operations on the LazyProxy instance will trigger
         the loading of the proxied object.
    """

    def __init__(self) -> None:
        self.__proxied: T | None = None

    def __getattr__(self, attr: str) -> object:
        return getattr(self.__get_proxied__(), attr)

    def __repr__(self) -> str:
        return repr(self.__get_proxied__())

    def __dir__(self) -> Iterable[str]:
        return self.__get_proxied__().__dir__()

    def __get_proxied__(self) -> T:
        proxied = self.__proxied
        if proxied is not None:
            return proxied

        self.__proxied = proxied = self.__load__()
        return proxied

    def __set_proxied__(self, value: T) -> None:
        self.__proxied = value

    def __as_proxied__(self) -> T:
        """Helper method that returns the current proxy, typed as the loaded object"""
        return cast(T, self)

    @abstractmethod
    def __load__(self) -> T:
        ...


JSON = Union[Dict[str, Any], List[Dict[str, Any]]]
MaybeHeaders = Optional[Headers]
MaybeJson = Optional[JSON]
MaybeBytes = Optional[bytes]
MaybeText = Optional[str]

from typing import List, Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class Owner(BaseModel):
    login: str = Field(...)
    id: int = Field(...)
    node_id: str = Field(...)
    avatar_url: str = Field(...)
    gravatar_id: Optional[str] = Field(default=None)
    url: str = Field(...)
    html_url: str = Field(...)
    followers_url: str = Field(...)
    following_url: str = Field(...)
    gists_url: str = Field(...)
    starred_url: str = Field(...)
    subscriptions_url: str = Field(...)
    organizations_url: str = Field(...)
    repos_url: str = Field(...)
    events_url: str = Field(...)
    received_events_url: str = Field(...)
    type: str = Field(...)
    site_admin: bool = Field(...)

class Permissions(BaseModel):
    admin: bool = Field(...)
    maintain: bool = Field(...)
    push: bool = Field(...)
    triage: bool = Field(...)
    pull: bool = Field(...)

class GitHubRepoFull(BaseModel):
    id: int = Field(...)
    node_id: str = Field(...)
    name: str = Field(...)
    full_name: str = Field(...)
    private: bool = Field(...)
    owner: Owner = Field(...)
    html_url: str = Field(...)
    description: Optional[str] = Field(default=None)
    fork: bool = Field(...)
    url: str = Field(...)
    forks_url: Optional[str] = Field(default=None)
    keys_url: Optional[str] = Field(default=None)
    collaborators_url: Optional[str] = Field(default=None)
    teams_url: Optional[str] = Field(default=None)
    hooks_url: Optional[str] = Field(default=None)
    issue_events_url: Optional[str] = Field(default=None)
    events_url: Optional[str] = Field(default=None)
    assignees_url: Optional[str] = Field(default=None)
    branches_url: Optional[str] = Field(default=None)
    tags_url: Optional[str] = Field(default=None)
    blobs_url: Optional[str] = Field(default=None)
    git_tags_url: Optional[str] = Field(default=None)
    git_refs_url: Optional[str] = Field(default=None)
    trees_url: Optional[str] = Field(default=None)
    statuses_url: Optional[str] = Field(default=None)
    languages_url: Optional[str] = Field(default=None)
    stargazers_url: Optional[str] = Field(default=None)
    contributors_url: Optional[str] = Field(default=None)
    subscribers_url: Optional[str] = Field(default=None)
    subscription_url: Optional[str] = Field(default=None)
    commits_url: str = Field(...)
    git_commits_url: str = Field(...)
    comments_url: Optional[str] = Field(default=None)
    issue_comment_url: Optional[str] = Field(default=None)
    contents_url: str = Field(...)
    compare_url: Optional[str] = Field(default=None)
    merges_url: Optional[str] = Field(default=None)
    archive_url: Optional[str] = Field(default=None)
    downloads_url: Optional[str] = Field(default=None)
    issues_url: Optional[str] = Field(default=None)
    pulls_url: Optional[str] = Field(default=None)
    milestones_url: Optional[str] = Field(default=None)
    notifications_url: Optional[str] = Field(default=None)
    labels_url: Optional[str] = Field(default=None)
    releases_url: Optional[str] = Field(default=None)
    deployments_url: Optional[str] = Field(default=None)
    created_at: str = Field(...)
    updated_at: str = Field(...)
    pushed_at: str = Field(...)
    git_url: str = Field(...)
    ssh_url: str = Field(...)
    clone_url: str = Field(...)
    svn_url: str = Field(...)
    homepage: Optional[str] = Field(default=None)
    size: int = Field(...)
    stargazers_count: int = Field(...)
    watchers_count: int = Field(...)
    language: Optional[str] = Field(default=None)
    has_issues: bool = Field(...)
    has_projects: bool = Field(...)
    has_downloads: bool = Field(...)
    has_wiki: bool = Field(...)
    has_pages: bool = Field(...)
    has_discussions: bool = Field(...)
    forks_count: int = Field(...)
    mirror_url: Optional[str] = Field(default=None)
    archived: bool = Field(...)
    disabled: bool = Field(...)
    open_issues_count: int = Field(...)
    license: Optional[str] = Field(default=None)
    allow_forking: bool = Field(...)
    is_template: bool = Field(...)
    web_commit_signoff_required: bool = Field(...)
    topics: List[str] = Field(default_factory=list)
    visibility: str = Field(...)
    forks: int = Field(...)
    open_issues: int = Field(...)
    watchers: int = Field(...)
    default_branch: str = Field(...)
    permissions: Permissions = Field(...)
    allow_squash_merge: bool = Field(...)
    allow_merge_commit: bool = Field(...)
    allow_rebase_merge: bool = Field(...)
    allow_auto_merge: bool = Field(...)
    delete_branch_on_merge: bool = Field(...)
    allow_update_branch: bool = Field(...)
    use_squash_pr_title_as_default: bool = Field(...)
    squash_merge_commit_message: str = Field(...)
    squash_merge_commit_title: str = Field(...)
    merge_commit_message: str = Field(...)
    merge_commit_title: str = Field(...)
    network_count: int = Field(...)
    subscribers_count: int = Field(...)


class GithubRepo(BaseModel):
    name: str
    full_name: str
    private: bool
    html_url: str
    description: Optional[str] = None
    fork: bool
    url: str
    created_at: str
    updated_at: str
    pushed_at: str
    homepage: Optional[str] = None
    size: int
    stargazers_count: int
    watchers_count: int
    language: Optional[str] = None
    forks_count: int
    open_issues_count: int
    master_branch: Optional[str] = None
    default_branch: str
    score: float

class CreateRepo(BaseModel):
    name: str
    description: Optional[str] = None
    private: bool = False
    
    

class UserSignUp(BaseModel):
    name: str
    email: str
    password: str
    picture: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserConfirmForgot(BaseModel):
    username: str
    code: str
    password: str


class AuthenticationResult(BaseModel):
    AccessToken: str
    ExpiresIn: int
    TokenType: str
    RefreshToken: str
    IdToken: str
    
    

class AuthResult(BaseModel):
    """- AuthResult
        - username
        - password
        - registry
    """
    username: str
    
    password: str
    registry: str


class ConnectionParams(BaseModel):
    """
    - ConnectionParams
        -  repo: repo name
        -  image: image name
        -   name: name of the service
    """
    repo: str
    image: str
    name: str


class ServiceParams(BaseModel):
    """
    - ServiceParams
        -  name: name of the service
        -  repo: repo name
        -  image: image name
        -  port: port number
    """
    name: str
    repo: str
    image: str
    port: int
    
    
class AppRunnerCreateService(BaseModel):
    service_name: str
    