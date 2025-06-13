#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/23
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : chroma
# @Software: PyCharm
import asyncio
import inspect
from typing import List, Optional

import chromadb
from chromadb import QueryResult

from domain.enums.chroma_mode import ChromaMode
from domain.entity.document import Document, DocumentMeta
from extensions.vector.base_vector import BaseVector
from setting.setting import get_we0_index_settings

settings = get_we0_index_settings()


class Chroma(BaseVector):

    def __init__(self):
        self.client: None = None
        self.collection_name: str | None = None

    @staticmethod
    def get_client():
        return None

    async def init(self):
        if self.client is None:
            chroma = settings.vector.chroma
            match chroma.mode:
                case ChromaMode.MEMORY:
                    self.client = chromadb.Client()
                case ChromaMode.DISK:
                    self.client = chromadb.PersistentClient(path=chroma.disk.path)
                case ChromaMode.REMOTE:
                    self.client = await chromadb.AsyncHttpClient(
                        host=chroma.remote.host, port=chroma.remote.port, ssl=chroma.remote.ssl
                    )
                case _:
                    raise ValueError(f'Unknown chroma mode: {chroma.mode}')
            dimension = await self.get_dimension()
            self.collection_name = self.dynamic_collection_name(dimension)
            await self._execute_async_or_thread(func=self.client.get_or_create_collection, name=self.collection_name)

    async def create(self, documents: List[Document]):
        collection = await self._execute_async_or_thread(
            func=self.client.get_or_create_collection,
            name=self.collection_name
        )
        ids = [document.meta.segment_id for document in documents]
        vectors = [document.vector for document in documents]
        metas = [document.meta.model_dump(exclude_none=True) for document in documents]
        contents = [document.content for document in documents]
        await self._execute_async_or_thread(
            func=collection.upsert, ids=ids, embeddings=vectors, metadatas=metas, documents=contents
        )

    async def upsert(self, documents: List[Document]):
        repo_id = documents[0].meta.repo_id
        file_ids = list(set(document.meta.file_id for document in documents))
        await self.delete(repo_id, file_ids)
        await self.create(documents)

    async def all_meta(self, repo_id: str) -> List[DocumentMeta]:
        collection = await self._execute_async_or_thread(
            func=self.client.get_or_create_collection,
            name=self.collection_name
        )
        results: QueryResult = await self._execute_async_or_thread(
            func=collection.get, where={
                'repo_id': {
                    '$eq': repo_id
                }
            }
        )
        metadatas = results.get('metadatas', [])
        if len(metadatas) == 0:
            return []
        metas = metadatas[0]
        return [DocumentMeta.model_validate(meta) for meta in metas]

    async def drop(self, repo_id: str):
        collection = await self._execute_async_or_thread(
            func=self.client.get_or_create_collection,
            name=self.collection_name
        )
        await self._execute_async_or_thread(
            func=collection.delete, where={
                'repo_id': {
                    "$eq": repo_id
                }
            }
        )

    async def delete(self, repo_id: str, file_ids: List[str]):
        collection = await self._execute_async_or_thread(
            func=self.client.get_or_create_collection,
            name=self.collection_name
        )
        await self._execute_async_or_thread(collection.delete, where={
            "$and": [
                {"repo_id": {"$eq": repo_id}},
                {"file_id": {"$in": file_ids}}
            ]
        })

    async def search_by_vector(
            self,
            repo_id: str,
            file_ids: Optional[List[str]],
            query_vector: List[float],
            top_k: int = 5,
            score_threshold: float = 0.0
    ) -> List[Document]:
        collection = await self._execute_async_or_thread(
            func=self.client.get_or_create_collection,
            name=self.collection_name
        )

        if not file_ids:
            where = {
                'repo_id': {
                    '$eq': repo_id
                }
            }
        else:
            where = {
                "$and": [
                    {"repo_id": {"$eq": repo_id}},
                    {"file_id": {"$in": file_ids}}
                ]
            }
        results: QueryResult = await self._execute_async_or_thread(
            func=collection.query, query_embeddings=query_vector, n_results=top_k, where=where
        )
        ids = results.get('ids', [])
        if len(ids) == 0:
            return []
        idx = ids[0]
        metas = results.get('metadatas', [])[0]
        distances = results.get('distances', [])[0]
        contents = results.get('documents', [])[0]

        documents: List[Document] = []
        for index in range(len(idx)):
            distance = distances[index]
            metadata = dict(metas[index])
            if distance >= score_threshold:
                metadata["score"] = distance
                metadata["content"] = contents[index]
                document = Document(
                    meta=DocumentMeta.model_validate(metadata),
                )
                documents.append(document)

        return sorted(documents, key=lambda x: x.meta.score)

    @staticmethod
    async def _execute_async_or_thread(func, *args, **kwargs):
        if inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func):
            return await func(*args, **kwargs)
        else:
            return await asyncio.to_thread(func, *args, **kwargs)
