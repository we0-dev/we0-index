#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/19
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : embeddings
# @Software: PyCharm
from typing import Union, List, Iterable, Optional

from openai.types import CreateEmbeddingResponse

from .client import AsyncClient


class AsyncEmbeddings:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def create(
            self,
            input: Union[str, List[str], Iterable[int], Iterable[Iterable[int]]],
            model: str = 'jina-embeddings-v2-base-code',
            normalized: Optional[bool] = None,
            embedding_type: Optional[str] = None,
            task: Optional[str] = None,
            late_chunking: Optional[bool] = None,
            dimensions: Optional[int] = None,
    ) -> CreateEmbeddingResponse:
        request_json = {
            'input': input,
            'model': model
        }
        if normalized:
            request_json['normalized'] = normalized
        if embedding_type:
            request_json['embedding_type'] = embedding_type
        if task:
            request_json['task'] = task
        if late_chunking:
            request_json['late_chunking'] = late_chunking
        if dimensions:
            request_json['dimensions'] = dimensions
        response = await self.client.post(
            '/embeddings', json=request_json,
            headers={'Authorization': f'Bearer {self.client.api_key}'}
        )
        return CreateEmbeddingResponse.model_validate(response.json())
