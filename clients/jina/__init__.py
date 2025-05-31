#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/19
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : __init__.py
# @Software: PyCharm
from clients.jina.client import AsyncClient
from clients.jina.embeddings import AsyncEmbeddings

__all__ = [
    'AsyncClient',
    'AsyncEmbeddings',
]
