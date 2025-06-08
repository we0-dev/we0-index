#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
from typing import List, Optional
from urllib.parse import quote

import aiofiles
from fastapi import APIRouter
from git import Repo
from loguru import logger

from domain.entity.blob import Blob
from domain.entity.document import Document
from domain.entity.task_context import TaskContext
from domain.request.git_index_request import GitIndexRequest
from domain.response.add_index_response import AddIndexResponse, FileInfoResponse
from domain.result.result import Result
from extensions.ext_manager import ExtManager
from setting.setting import get_we0_index_settings
from utils.git_parse import parse_git_url
from utils.helper import Helper
from utils.mimetype_util import guess_mimetype_and_extension
from utils.vector_helper import VectorHelper
from asyncio import Semaphore
git_router = APIRouter()
settings = get_we0_index_settings()
async_semaphore = Semaphore(100)

async def _process_file(uid: str, repo_id: str, repo_path: str, base_dir, relative_path: str) -> FileInfoResponse:
    logger.info(f'Processing file {relative_path}')
    mimetype, extension = guess_mimetype_and_extension(relative_path)
    file_id = Helper.generate_fixed_uuid(f"{uid}:{repo_path}:{relative_path}")
    file_path = os.path.join(base_dir, relative_path)
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()

    task_context = TaskContext(
        repo_id=repo_id,
        file_id=file_id,
        relative_path=relative_path,
        blob=Blob.from_data(
            data=content,
            mimetype=mimetype,
            extension=extension
        )
    )

    try:
        async with async_semaphore:
            documents: List[Document] = await VectorHelper.build_and_embedding_segment(task_context)
            if documents:
                await ExtManager.vector.upsert(documents)
    except Exception as e:
        raise e

    return FileInfoResponse(
        file_id=file_id,
        relative_path=relative_path
    )


def _prepare_repo_url_with_auth(repo_url: str, username: Optional[str] = None, password: Optional[str] = None,
                                access_token: Optional[str] = None) -> str:
    """
    为私有仓库准备带有认证信息的 URL
    对用户名和密码进行 URL 编码，以处理包含特殊字符（如 @ 符号）的情况
    支持三种认证方式：
    1. access_token: 使用个人访问令牌（推荐）
    2. username + password: 使用用户名和密码
    3. 无认证: 公开仓库
    """
    if repo_url.startswith('https://'):
        if access_token:
            # 使用 access_token 进行认证
            # 对于大多数 Git 服务提供商（GitHub, GitLab 等），使用 token 作为用户名，密码可以为空或使用 token
            encoded_token = quote(access_token, safe='')
            url_without_protocol = repo_url[8:]
            # 使用 token 作为用户名，密码为 'x-oauth-basic'（GitHub）或空字符串
            return f'https://{encoded_token}:x-oauth-basic@{url_without_protocol}'
        elif username and password:
            # 对用户名和密码进行 URL 编码以处理特殊字符
            encoded_username = quote(username, safe='')
            encoded_password = quote(password, safe='')
            # 使用编码后的用户名和密码
            url_without_protocol = repo_url[8:]
            return f'https://{encoded_username}:{encoded_password}@{url_without_protocol}'
    return repo_url


async def clone_and_index(git_index_request: GitIndexRequest) -> Result[AddIndexResponse]:
    """
    Tool parameters must be in standard JSON format!
    "git_index_request": {
        "xxx": "xxx"
    }
    克隆 Git 仓库并对所有文件进行索引
    支持私有仓库访问:
    - Access Token 认证 (推荐): 提供 access_token 参数
    - SSH 密钥认证: 使用 git@github.com:user/repo.git 格式的 URL，可选择提供 ssh_key_path
    - HTTPS + 用户名密码: 提供 username 和 password 参数
    """
    try:
        if not git_index_request.uid:
            git_index_request.uid = 'default_uid'

        domain, owner, repo = parse_git_url(git_index_request.repo_url)
        repo_abs_path = f'{domain}/{owner}/{repo}'
        repo_id = Helper.generate_fixed_uuid(f"{git_index_request.uid}{repo_abs_path}:")

        # 准备认证后的仓库 URL
        auth_repo_url = _prepare_repo_url_with_auth(
            git_index_request.repo_url,
            git_index_request.username,
            git_index_request.password,
            git_index_request.access_token
        )

        file_count = 0  # 初始化 file_count 变量

        async with aiofiles.tempfile.TemporaryDirectory() as tmp_dir:
            try:
                await asyncio.to_thread(
                    Repo.clone_from,
                    auth_repo_url,
                    tmp_dir
                )
            except Exception as e:
                logger.error(f'{type(e).__name__}: {e}')
                raise e
            # 遍历并处理文件
            tasks = []
            for root, dirs, files in os.walk(tmp_dir):
                # 忽略 .git 等隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if not file.startswith('.'):
                        relative_path = os.path.relpath(os.path.join(root, file), start=tmp_dir)
                        tasks.append(asyncio.create_task(_process_file(
                            uid=git_index_request.uid,
                            repo_id=repo_id,
                            repo_path=repo_abs_path,
                            base_dir=tmp_dir,
                            relative_path=relative_path
                        )))
            for task in asyncio.as_completed(tasks):
                await task
                file_count += 1

            logger.info(f"Successfully processed {file_count} files from repository {repo_abs_path}")

        return Result.ok(data=AddIndexResponse(
            repo_id=repo_id,
            file_infos=[]
        ))
    except Exception as e:
        logger.exception(e)
        return Result.failed(message=f"{type(e).__name__}: {e}")


git_router.add_api_route('/clone_and_index', clone_and_index, methods=['POST'], response_model=Result[AddIndexResponse])
