#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/22
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : qdrant
# @Software: PyCharm

from typing import List, Optional

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.exceptions import UnexpectedResponse

from domain.emuns.qdrant_mode import QdrantMode
from domain.entity.document import Document, DocumentMeta
from extensions.vector.base_vector import BaseVector
from setting.setting import get_we0_index_settings

settings = get_we0_index_settings()


class Qdrant(BaseVector):

    def __init__(self):
        self.client = self.get_client()
        self.collection_name: str | None = None

    @staticmethod
    def get_client():
        qdrant = settings.vector.qdrant
        match qdrant.mode:
            case QdrantMode.MEMORY:
                return AsyncQdrantClient(location=':memory:')
            case QdrantMode.DISK:
                return AsyncQdrantClient(path=qdrant.disk.path)
            case QdrantMode.REMOTE:
                return AsyncQdrantClient(host=qdrant.remote.host, port=qdrant.remote.port)
            case _:
                raise ValueError(f'Unknown qdrant mode: {qdrant.mode}')

    async def init(self):
        collection_names = []
        dimension = await self.get_dimension()
        self.collection_name = self.dynamic_collection_name(dimension)
        collections: rest.CollectionsResponse = await self.client.get_collections()
        for collection in collections.collections:
            collection_names.append(collection.name)
        if self.collection_name not in collection_names:
            vectors_config = rest.VectorParams(
                size=dimension,
                distance=rest.Distance.COSINE
            )
            hnsw_config = rest.HnswConfigDiff(
                m=0,
                payload_m=16,
                ef_construct=100,
                full_scan_threshold=10000,
                max_indexing_threads=0,
                on_disk=False,
            )
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config,
                hnsw_config=hnsw_config,
                timeout=30
            )
            if settings.vector.qdrant.mode != QdrantMode.DISK:
                await self.client.create_payload_index(
                    self.collection_name, 'repo_id', field_schema=rest.PayloadSchemaType.KEYWORD
                )
                await self.client.create_payload_index(
                    self.collection_name, 'file_id', field_schema=rest.PayloadSchemaType.KEYWORD
                )

    async def create(self, documents: List[Document]):
        repo_id = documents[0].meta.repo_id
        print_structs = []
        for document in documents:
            document.meta.content = document.content  # qdrant，就只能存三个值id vector payload，所以只能把content转到meta
        for document in documents:
            document.meta.repo_id = repo_id
            print_structs.append(rest.PointStruct(
                id=document.meta.segment_id,
                vector=document.vector,
                payload=document.meta.model_dump(exclude_none=True),
            ))

        await self.client.upsert(collection_name=self.collection_name, points=print_structs)

    async def upsert(self, documents: List[Document]):
        repo_id = documents[0].meta.repo_id
        file_ids = list(set(document.meta.file_id for document in documents))
        await self.delete(repo_id, file_ids)
        await self.create(documents)

    async def all_meta(self, repo_id: str) -> List[DocumentMeta]:
        scroll_filter = rest.Filter(
            must=[
                rest.FieldCondition(
                    key="repo_id",
                    match=rest.MatchValue(value=repo_id),
                ),
            ],
        )

        records, next_offset = await self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=scroll_filter,
            limit=100,
            with_payload=True
        )

        while next_offset:
            scroll_records, next_offset = await self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=scroll_filter,
                limit=100,
                with_payload=True,
                offset=next_offset
            )
            records.extend(scroll_records)
        return [DocumentMeta.model_validate(record.payload) for record in records]

    async def drop(self, repo_id: str):
        filter_selector = rest.Filter(
            must=[
                rest.FieldCondition(
                    key="repo_id",
                    match=rest.MatchValue(value=repo_id),
                ),
            ],
        )
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=filter_selector
            )
        except UnexpectedResponse as e:
            if e.status_code == 404:
                return
            raise e

    async def delete(self, repo_id: str, file_ids: List[str]):
        filter_selector = rest.Filter(
            must=[
                rest.FieldCondition(
                    key="repo_id",
                    match=rest.MatchValue(value=repo_id),
                ),
                rest.FieldCondition(
                    key="file_id",
                    match=rest.MatchAny(any=file_ids),
                )
            ],
        )
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=filter_selector
            )
        except UnexpectedResponse as e:
            if e.status_code == 404:
                return
            raise e
        except Exception as e:
            raise e

    async def search_by_vector(
            self,
            repo_id: str,
            file_ids: Optional[List[str]],
            query_vector: List[float],
            top_k: int = 5,
            score_threshold: float = 0.0
    ) -> List[Document]:

        query_filter = rest.Filter(
            must=[
                rest.FieldCondition(
                    key="repo_id",
                    match=rest.MatchValue(value=repo_id),
                ),
            ],
        )
        # 如果 file_ids 不为空，添加 file_id 的过滤条件
        if file_ids:
            query_filter.must.append(
                rest.FieldCondition(
                    key="file_id",
                    match=rest.MatchAny(any=file_ids),
                )
            )
        response: rest.QueryResponse = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=True,
            score_threshold=score_threshold,
        )
        documents: List[Document] = []
        for point in response.points:
            meta = DocumentMeta.model_validate(point.payload)
            meta.score = point.score
            documents.append(Document(meta=meta))
        return documents
