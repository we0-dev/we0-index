#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/14
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : base_vector
# @Software: PyCharm
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entity.document import Document, DocumentMeta
from models.model_factory import ModelFactory
from setting.setting import get_we0_index_settings

settings = get_we0_index_settings()


class BaseVector(ABC):

    @staticmethod
    @abstractmethod
    def get_client():
        raise NotImplementedError

    @abstractmethod
    async def init(self):
        raise NotImplementedError

    @abstractmethod
    async def create(self, documents: List[Document]):
        raise NotImplementedError

    @abstractmethod
    async def upsert(self, documents: List[Document]):
        raise NotImplementedError

    @abstractmethod
    async def all_meta(self, repo_id: str) -> List[DocumentMeta]:
        raise NotImplementedError

    @abstractmethod
    async def drop(self, repo_id: str):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, repo_id: str, file_ids: List[str]):
        raise NotImplementedError

    @abstractmethod
    async def search_by_vector(
            self,
            repo_id: str,
            file_ids: Optional[List[str]],
            query_vector: List[float],
            top_k: int = 5,
            score_threshold: float = 0.0
    ) -> List[Document]:
        raise NotImplementedError

    @staticmethod
    def dynamic_collection_name(dimension: int) -> str:
        return f'we0_index_{settings.vector.embedding_model}_{dimension}'.replace('-', '_')

    # TODO 以后这边应该从仓库数据表中读取用户的`model_provider`和`model_name`
    #  前期先全部使用`openai`的`text-embedding-3-small`
    @classmethod
    async def get_embedding_model(cls):
        return await ModelFactory.get_model(
            model_provider=settings.vector.embedding_provider,
            model_name=settings.vector.embedding_model
        )

    @classmethod
    async def get_completions_model(cls):
        return await ModelFactory.get_model(
            model_provider=settings.vector.chat_provider,
            model_name=settings.vector.chat_model
        )

    @classmethod
    async def get_dimension(cls) -> int:
        embedding_model = await cls.get_embedding_model()
        vector_data_list = await embedding_model.create_embedding(['get_embedding_dimension'])
        dimension = len(vector_data_list[0])
        return dimension
