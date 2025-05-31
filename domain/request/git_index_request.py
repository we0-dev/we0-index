from pydantic import BaseModel


class GitIndexRequest(BaseModel):
    uid: str | None = None
    repo_url: str
