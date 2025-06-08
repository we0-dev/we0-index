#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/23
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : vector_helper
# @Software: PyCharm
import asyncio
import uuid
from typing import List

from fastapi import APIRouter
from loguru import logger

from domain.entity.document import Document, DocumentMeta
from domain.entity.task_context import TaskContext
from extensions.ext_manager import ExtManager
from loader.repo_loader import RepoLoader
from models.model_factory import ModelInstance
from prompt.prompt import SystemMessageTemplate
from setting.setting import get_we0_index_settings
from utils.helper import Helper

vector_router = APIRouter()

settings = get_we0_index_settings()


class VectorHelper:
    @staticmethod
    async def code2description(document: Document, chat_model: ModelInstance):
        document.meta.description = await chat_model.create_completions(
            messages=SystemMessageTemplate.ANALYZE_CODE_MESSAGE_TEMPLATE(document.content)
        )

    @staticmethod
    async def build_and_embedding_segment(task_context: TaskContext) -> List[Document]:
        try:
            documents: List[Document] = [
                Document(
                    content=segment.code,
                    meta=DocumentMeta(
                        repo_id=task_context.repo_id,
                        file_id=task_context.file_id,
                        segment_id=f"{uuid.uuid4()}",
                        relative_path=task_context.relative_path,
                        start_line=segment.start,
                        end_line=segment.end,
                        segment_block=segment.block,
                        segment_hash=Helper.generate_text_hash(segment.code),
                        segment_cl100k_base_token=Helper.calculate_tokens(segment.code),
                        segment_o200k_base_token=Helper.calculate_tokens(segment.code, 'o200k_base')
                    )
                ) async for segment in RepoLoader.load_blob(task_context.blob)
            ]
        except UnicodeDecodeError as e:
            logger.error(e)
            documents = []
        if documents:
            embedding_model: ModelInstance = await ExtManager.vector.get_embedding_model()
            if settings.vector.code2desc:
                chat_model: ModelInstance = await ExtManager.vector.get_completions_model()
                await asyncio.wait([
                    asyncio.create_task(VectorHelper.code2description(document=document, chat_model=chat_model))
                    for document in documents
                ])
                vector_data: List[List[float]] = await embedding_model.create_embedding(
                    [
                        f"'{document.meta.relative_path}'\n'{document.meta.description}'\n{document.content}"
                        for document in documents
                    ]
                )
            else:
                vector_data: List[List[float]] = await embedding_model.create_embedding(
                    [
                        f"'{document.meta.relative_path}'\n{document.content}" for document in documents
                    ]
                )
            for index, document in enumerate(documents):
                document.vector = vector_data[index]
        return documents
