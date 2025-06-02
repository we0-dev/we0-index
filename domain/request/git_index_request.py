from pydantic import BaseModel
from typing import Optional

class GitIndexRequest(BaseModel):
    uid: str | None = None
    repo_url: str
    # 私有仓库认证字段
    username: Optional[str] = None  # 用户名
    password: Optional[str] = None  # 密码或个人访问令牌
    access_token: Optional[str] = None  # 访问令牌（GitHub/GitLab Personal Access Token）