#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/10/11
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : vector_router
# @Software: PyCharm
import asyncio
from typing import Annotated
from typing import List

from fastapi import APIRouter, UploadFile
from fastapi.params import File, Form

from domain.entity.blob import Blob
from domain.entity.document import DocumentMeta, Document
from domain.entity.task_context import TaskContext
from domain.request.add_index_request import AddIndexRequest, AddFileInfo
from domain.request.all_index_request import AllIndexRequest
from domain.request.delete_index_request import DeleteIndexRequest
from domain.request.drop_index_request import DropIndexRequest
from domain.request.retrieval_request import RetrievalRequest
from domain.response.add_index_by_file_response import AddIndexByFileResponse
from domain.response.add_index_response import AddIndexResponse, FileInfoResponse
from domain.result.result import Result
from extensions.ext_manager import ExtManager
from models.model_factory import ModelInstance
from setting.setting import get_we0_index_settings
from utils.helper import Helper
from utils.mimetype_util import guess_mimetype_and_extension
from utils.vector_helper import VectorHelper

vector_router = APIRouter()

settings = get_we0_index_settings()


async def _upsert_index(uid: str, repo_abs_path: str, repo_id: str, file_info: AddFileInfo) -> FileInfoResponse:
    mimetype, extension = guess_mimetype_and_extension(file_info.relative_path)
    file_id = Helper.generate_fixed_uuid(
        f"{uid}:{repo_abs_path}:{file_info.relative_path}"
    )

    task_context = TaskContext(
        repo_id=repo_id,
        file_id=file_id,
        relative_path=file_info.relative_path,
        blob=Blob.from_data(
            data=file_info.content,
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
        relative_path=file_info.relative_path
    )


@vector_router.post("/upsert_index", response_model=Result[AddIndexResponse])
async def upsert_index(add_index_request: AddIndexRequest):
    """
    新增或追加索引
    请务必使用JSON.stringify对文本进行转义，确保格式正确，否则AST结构将被破坏\n
    `fs.readFile(filePath, 'utf8', (err, fileContent) => {const jsonStr = JSON.stringify(data);}`\n
    """
    repo_id = Helper.generate_fixed_uuid(f"{add_index_request.uid}:{add_index_request.repo_abs_path}")

    tasks = [
        asyncio.create_task(_upsert_index(
            uid=add_index_request.uid,
            repo_abs_path=add_index_request.repo_abs_path,
            repo_id=repo_id,
            file_info=file_info
        )) for file_info in add_index_request.file_infos
    ]
    file_infos = [await task for task in asyncio.as_completed(tasks)]
    return Result.ok(data=AddIndexResponse(repo_id=repo_id, file_infos=file_infos))


@vector_router.post('/upsert_index_by_file', response_model=Result[AddIndexByFileResponse])
async def upsert_index_by_file(
        uid: Annotated[str, Form(description='Unique ID')],
        repo_abs_path: Annotated[str, Form(description='Repository Absolute Path')],
        relative_path: Annotated[str, Form(description='File Relative Path')],
        file: UploadFile = File(...),
):
    """
    新增或追加索引(通过文件)
    """
    repo_id = Helper.generate_fixed_uuid(f"{uid}:{repo_abs_path}")
    mimetype, extension = guess_mimetype_and_extension(relative_path)

    file_id = Helper.generate_fixed_uuid(f"{uid}:{repo_abs_path}:{relative_path}")

    task_context = TaskContext(
        repo_id=repo_id,
        file_id=file_id,
        relative_path=relative_path,
        blob=Blob.from_data(
            data=await file.read(),
            mimetype=mimetype,
            extension=extension
        )
    )
    try:
        documents: List[Document] = await VectorHelper.build_and_embedding_segment(task_context)
        if documents:
            await ExtManager.vector.upsert(documents)
            return Result.ok(data=AddIndexByFileResponse(repo_id=repo_id, file_id=file_id))
        else:
            return Result.failed(message=f"Not Content")
    except Exception as e:
        return Result.failed(message=f"{type(e).__name__}: {e}")


@vector_router.post('/drop_index', response_model=Result)
async def drop_index(drop_index_request: DropIndexRequest):
    """
    删除索引的全部向量
    """
    try:
        await ExtManager.vector.drop(repo_id=drop_index_request.repo_id)
        return Result.ok()
    except Exception as e:
        return Result.failed(message=f"{type(e).__name__}: {e}")


@vector_router.post('/delete_index', response_model=Result)
async def delete_index(delete_index_request: DeleteIndexRequest):
    """
    删除索引的指定向量
    """
    try:
        await ExtManager.vector.delete(repo_id=delete_index_request.repo_id, file_ids=delete_index_request.file_ids)
        return Result.ok()
    except Exception as e:
        return Result.failed(message=f"{type(e).__name__}: {e}")


@vector_router.post('/all_index', response_model=Result)
async def all_index(all_index_request: AllIndexRequest):
    try:
        all_meta = await ExtManager.vector.all_meta(repo_id=all_index_request.repo_id)
        return Result.ok(data=all_meta)
    except Exception as e:
        return Result.failed(message=f"{type(e).__name__}: {e}")


async def retrieval(
        retrieval_request: RetrievalRequest
) -> Result[List[DocumentMeta]]:
    """
    Tool parameters must be in standard JSON format!
    "retrieval_request": {
        "xxx": "xxx"
    }
    相似度匹配，从整个仓库或指定仓库的部分文件
    """
    try:
        embedding_model: ModelInstance = await ExtManager.vector.get_embedding_model()
        vector_data = await embedding_model.create_embedding([retrieval_request.query])
        documents = await ExtManager.vector.search_by_vector(
            repo_id=retrieval_request.repo_id, file_ids=retrieval_request.file_ids, query_vector=vector_data[0]
        )
        retrieval_segment_list = [document.meta for document in documents]
        return Result.ok(data=retrieval_segment_list)
    except Exception as e:
        return Result.failed(message=f"{type(e).__name__}: {e}")


vector_router.add_api_route('/retrieval', retrieval, methods=['POST'], response_model=Result[List[DocumentMeta]])
