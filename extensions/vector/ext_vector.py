#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/14
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : ext_vector
# @Software: PyCharm
from typing import List, Optional

from loguru import logger

from domain.emuns.vector_type import VectorType
from domain.entity.document import Document, DocumentMeta
from extensions.vector.base_vector import BaseVector
from setting.setting import We0IndexSettings, get_we0_index_settings

settings: We0IndexSettings = get_we0_index_settings()


class Vector:

    def __init__(self):
        self.vector_runner: BaseVector | None = None

    async def create(self, documents: List[Document]):
        try:
            await self.vector_runner.create(documents)
        except Exception as e:
            logger.error(e)
            raise e

    async def upsert(self, documents: List[Document]):
        try:
            await self.vector_runner.upsert(documents)
        except Exception as e:
            logger.error(e)
            raise e

    async def all_meta(self, repo_id: str) -> List[DocumentMeta]:
        try:
            return await self.vector_runner.all_meta(repo_id)
        except Exception as e:
            logger.error(e)
            raise e

    async def drop(self, repo_id: str):
        try:
            await self.vector_runner.drop(repo_id)
        except Exception as e:
            logger.error(e)
            raise e

    async def delete(self, repo_id: str, file_ids: List[str]):
        try:
            await self.vector_runner.delete(repo_id, file_ids)
        except Exception as e:
            logger.error(e)
            raise e

    async def search_by_vector(
            self, repo_id: str, file_ids: Optional[List[str]], query_vector: List[float], top_k: int = 5
    ) -> List[Document]:
        try:
            return await self.vector_runner.search_by_vector(repo_id, file_ids, query_vector, top_k)
        except Exception as e:
            logger.error(e)
            raise e

    async def init_app(self) -> None:
        vector_constructor = self.get_vector_factory(settings.vector.platform)
        self.vector_runner = vector_constructor()
        await self.vector_runner.init()

    @staticmethod
    def get_vector_factory(vector_type: VectorType) -> type[BaseVector]:
        match vector_type:
            case VectorType.PGVECTOR:
                from extensions.vector.pgvector import PgVector

                return PgVector
            case VectorType.QDRANT:
                from extensions.vector.qdrant import Qdrant

                return Qdrant
            case VectorType.CHROMA:
                from extensions.vector.chroma import Chroma

                return Chroma
            case _:
                raise ValueError(f"Unknown storage type: {vector_type}")

    def __getattr__(self, item):
        if self.vector_runner is None:
            raise RuntimeError("Vector clients is not initialized. Call init_app first.")
        return getattr(self.vector_runner, item)
