#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from typing import List

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

git_router = APIRouter()
settings = get_we0_index_settings()


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
        documents: List[Document] = await VectorHelper.build_and_embedding_segment(task_context)
        if documents:
            await ExtManager.vector.upsert(documents)
    except Exception as e:
        raise e

    return FileInfoResponse(
        file_id=file_id,
        relative_path=relative_path
    )


@git_router.post("/clone_and_index", response_model=Result[AddIndexResponse])
async def clone_and_index(git_index_request: GitIndexRequest):
    """
    克隆 Git 仓库并对所有文件进行索引
    """
    try:
        if not git_index_request.uid:
            git_index_request.uid = 'default_uid'
        domain, owner, repo = parse_git_url(git_index_request.repo_url)
        repo_abs_path = f'{domain}/{owner}/{repo}'
        repo_id = Helper.generate_fixed_uuid(f"{git_index_request.uid}{repo_abs_path}:")

        async with aiofiles.tempfile.TemporaryDirectory() as tmp_dir:
            Repo.clone_from(
                url=git_index_request.repo_url,
                to_path=tmp_dir
            )
            for root, dirs, files in os.walk(tmp_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if not file.startswith('.'):
                        relative_path = os.path.relpath(os.path.join(root, file), start=tmp_dir)
                        await _process_file(
                            uid=git_index_request.uid,
                            repo_id=repo_id,
                            repo_path=repo_abs_path,
                            base_dir=tmp_dir,
                            relative_path=relative_path
                        )
        return Result.ok(data=AddIndexResponse(
            repo_id=repo_id,
            file_infos=[]
        ))
    except Exception as e:
        logger.exception(e)
        return Result.failed(message=f"{type(e).__name__}: {e}")
