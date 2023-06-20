from typing import *

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

TemplatesAvailable = Literal["react", "vue", "flask","express","fastapi","php"]

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


class EnvironBrief(BaseModel):
    url: str
    ip: str
    container: str


class CreateRepo(BaseModel):
    name: str
    description: Optional[str] = None
    private: bool = False
    token:str
    

class DeployResponse(BaseModel):
    workspace: EnvironBrief
    preview: EnvironBrief
    repo: GitHubRepoFull


class RepoTemplateCreate(BaseModel):
    template_owner:str 
    template_repo: TemplatesAvailable
    name: str
    login: str
    token:str
    email: str