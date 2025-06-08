#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/14
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : pgvector
# @Software: PyCharm
import json
from typing import List, Optional

import numpy as np
from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import create_async_engine

from domain.entity.document import Document, DocumentMeta
from extensions.vector.base_vector import BaseVector
from setting.setting import get_we0_index_settings

settings = get_we0_index_settings()

SQL_CREATE_FILE_INDEX = lambda table_name: f"""
CREATE INDEX IF NOT EXISTS file_idx ON {table_name} (file_id);
"""
SQL_CREATE_REPO_FILE_INDEX = lambda table_name: f"""
CREATE INDEX IF NOT EXISTS repo_file_idx ON {table_name} (repo_id, file_id);
"""
SQL_CREATE_EMBEDDING_INDEX = lambda table_name: f"""
CREATE INDEX IF NOT EXISTS embedding_cosine_idx ON {table_name} 
USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
"""

SQL_CREATE_TABLE = lambda table_name, dimension: f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id UUID PRIMARY KEY,
    repo_id UUID NOT NULL,
    file_id UUID NOT NULL,
    content TEXT NOT NULL,
    meta JSONB NOT NULL,
    embedding vector({dimension}) NOT NULL
) USING heap;
"""


class PgVector(BaseVector):

    def __init__(self):
        self.client = self.get_client()
        self.table_name: str | None = None
        self.normalized: bool = False

    @staticmethod
    def get_client():
        pgvector = settings.vector.pgvector
        return create_async_engine(
            url=f"postgresql+psycopg://{pgvector.user}:{pgvector.password}@{pgvector.host}:{pgvector.port}/{pgvector.db}",
            echo=False,
        )

    async def init(self):
        async with self.client.begin() as conn:
            dimension = await self.get_dimension()
            if dimension > 2000:
                dimension = 2000
                self.normalized = True
            self.table_name = self.dynamic_collection_name(dimension)
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.execute(text(SQL_CREATE_TABLE(self.table_name, dimension)))
            await conn.execute(text(SQL_CREATE_REPO_FILE_INDEX(self.table_name)))
            await conn.execute(text(SQL_CREATE_FILE_INDEX(self.table_name)))
            await conn.execute(text(SQL_CREATE_EMBEDDING_INDEX(self.table_name)))

    async def _create(self, repo_id: str, documents: List[Document]):
        stmt = text(
            f"""
                INSERT INTO {self.table_name} (id, repo_id, file_id, content, meta, embedding) 
                VALUES (:id, :repo_id, :file_id, :content, :meta, :embedding)
                ON CONFLICT (id) DO UPDATE SET 
                    repo_id = EXCLUDED.repo_id,
                    file_id = EXCLUDED.file_id,
                    content = EXCLUDED.content,
                    meta = EXCLUDED.meta,
                    embedding = EXCLUDED.embedding
                """
        )
        parameters = []
        for doc in documents:
            if doc.meta is not None:
                if self.normalized:
                    vector = self.normalize_l2(doc.vector[:2000])
                else:
                    vector = doc.vector
                parameters.append({
                    'id': doc.meta.segment_id,
                    'repo_id': repo_id,
                    'file_id': doc.meta.file_id,
                    'content': doc.content,
                    'meta': doc.meta.model_dump_json(exclude={'score', 'content'}),
                    'embedding': vector,
                })

        return stmt, parameters

    async def create(self, documents: List[Document]):
        async with self.client.begin() as conn:
            repo_id = documents[0].meta.repo_id
            insert_stmt, insert_parameters = await self._create(repo_id, documents)
            await conn.execute(
                insert_stmt,
                insert_parameters
            )

    async def upsert(self, documents: List[Document]):
        repo_id = documents[0].meta.repo_id
        file_ids = list(set(document.meta.file_id for document in documents))
        async with self.client.begin() as conn:
            delete_stmt, delete_parameters = await self._delete(repo_id, file_ids)
            await conn.execute(
                delete_stmt,
                delete_parameters
            )
            insert_stmt, insert_parameters = await self._create(repo_id, documents)
            await conn.execute(
                insert_stmt,
                insert_parameters
            )

    async def all_meta(self, repo_id: str) -> List[DocumentMeta]:
        async with self.client.begin() as conn:
            sql_query = (
                f"SELECT meta "
                f"FROM {self.table_name} "
                f"WHERE repo_id = :repo_id"
            )
            result = await conn.execute(
                text(sql_query),
                {
                    "repo_id": repo_id,
                }
            )
            records = result.all()
        return [DocumentMeta.model_validate(meta[0]) for meta in records]

    async def drop(self, repo_id: str):
        async with self.client.begin() as conn:
            await conn.execute(
                text(
                    f"DELETE FROM {self.table_name} "
                    "WHERE repo_id = :repo_id"
                ),
                {'repo_id': repo_id}
            )

    async def _delete(self, repo_id: str, file_ids: List[str]):
        sql_query = (
            f"DELETE FROM {self.table_name} "
            "WHERE repo_id = :repo_id AND file_id = ANY(:file_ids) "
        )
        stmt = text(sql_query).bindparams(
            bindparam("file_ids", expanding=False)  # 关键点：禁止自动展开列表为多个参数
        )
        parameters = {'repo_id': repo_id, 'file_ids': file_ids}
        return stmt, parameters

    async def delete(self, repo_id: str, file_ids: List[str]):
        async with self.client.begin() as conn:
            delete_stmt, delete_parameters = await self._delete(repo_id, file_ids)
            await conn.execute(
                delete_stmt,
                delete_parameters
            )

    async def search_by_vector(
            self,
            repo_id: str,
            file_ids: Optional[List[str]],
            query_vector: List[float],
            top_k: int = 5,
            score_threshold: float = 0.0
    ) -> List[Document]:
        documents = []
        async with self.client.begin() as conn:
            # 基础 SQL 查询
            sql_query = (
                f"SELECT content, meta, embedding <=> :query_vector AS distance "
                f"FROM {self.table_name} "
                f"WHERE repo_id = :repo_id "
            )
            if self.normalized:
                query_vector = self.normalize_l2(query_vector[:2000])
            # 基础参数
            parameters = {
                "query_vector": json.dumps(query_vector),
                "repo_id": repo_id,
                "top_k": top_k
            }

            if file_ids:
                sql_query += "AND file_id = ANY(:file_ids) "
                parameters["file_ids"] = file_ids

            sql_query += "ORDER BY distance LIMIT :top_k"

            if file_ids:
                stmt = text(sql_query).bindparams(
                    bindparam("file_ids", expanding=False)
                )
            else:
                stmt = text(sql_query)

            result = await conn.execute(
                stmt,
                parameters
            )
            records = result.all()
            for record in records:
                content, meta, distance = record
                score = 1 - distance
                if score > score_threshold:
                    meta["score"] = score
                    meta['content'] = content
                    documents.append(Document(content=content, meta=DocumentMeta.model_validate(meta)))
        return documents

    @staticmethod
    def normalize_l2(x: List[float]) -> List[float]:
        x = np.array(x)
        if x.ndim == 1:
            norm = np.linalg.norm(x)
            if norm == 0:
                return x.tolist()
            return (x / norm).tolist()
        else:
            norm = np.linalg.norm(x, 2, axis=1, keepdims=True)
            return np.where(norm == 0, x, x / norm).tolist()
