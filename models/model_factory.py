#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/15
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : model_factory
# @Software: PyCharm
import asyncio
from typing import List, Tuple, Dict, Iterable

from openai.types import CreateEmbeddingResponse
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion

from clients import jina
from domain.emuns.model_provider import ModelType


class ModelInstance:

    def __init__(self, model_type: ModelType, model_name: str):
        self.model_type = model_type
        self.model_name = model_name

    def get_completions_client(self):
        match self.model_type:
            case ModelType.OPENAI:
                import openai
                return openai.AsyncClient().chat.completions
            case _:
                raise Exception(f"Unknown model type: {self.model_type}")

    def get_embedding_client(self):
        match self.model_type:
            case ModelType.OPENAI:
                import openai
                return openai.AsyncClient().embeddings
            case ModelType.JINA:
                return jina.AsyncClient().embeddings
            case _:
                raise Exception(f"Unknown model type: {self.model_type}")

    async def create_embedding(self, documents: List[str]) -> List[List[float]]:
        match self.model_type:
            case ModelType.OPENAI | ModelType.JINA:
                embedding_response: CreateEmbeddingResponse = await self.get_embedding_client().create(
                    input=documents, model=self.model_name
                )
                return [data.embedding for data in embedding_response.data]
            case _:
                raise Exception(f"Unknown model type: {self.model_type}")

    async def create_completions(self, messages: Iterable[ChatCompletionMessageParam]) -> str:
        match self.model_type:
            case ModelType.OPENAI:
                completions_response: ChatCompletion = await self.get_completions_client().create(
                    model=self.model_name, messages=messages
                )
                return completions_response.choices[0].message.content
            case _:
                raise Exception(f"Unknown model type: {self.model_type}")


class ModelFactory:
    _lock = asyncio.Lock()
    _instances: Dict[Tuple[ModelType, str], ModelInstance] = {}

    @classmethod
    async def get_model(cls, model_provider: ModelType, model_name: str) -> ModelInstance:
        key = (model_provider, model_name)
        if key not in ModelFactory._instances:
            async with cls._lock:
                if key not in ModelFactory._instances:
                    instance = ModelInstance(model_provider, model_name)
                    cls._instances[key] = instance
        return cls._instances[key]
