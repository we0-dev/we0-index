#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/19
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : jina
# @Software: PyCharm
import os
from typing import Optional

import httpx


class AsyncClient(httpx.AsyncClient):

    def __init__(
            self,
            base_url: Optional[str] = None,
            api_key: Optional[str] = None,
            timeout: Optional[int] = 300,
            *args, **kwargs
    ):
        if api_key is None:
            api_key = os.environ.get("JINA_API_KEY")
        if api_key is None:
            raise ValueError(
                "The api_key clients option must be set either by passing api_key to the clients or by setting the JINA_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("JINA_BASE_URL")
        if base_url is None:
            base_url = f"https://api.jina.ai/v1"

        super().__init__(base_url=base_url, timeout=timeout, *args, **kwargs)

        from .embeddings import AsyncEmbeddings
        self.embeddings = AsyncEmbeddings(self)
