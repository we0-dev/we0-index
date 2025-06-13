#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/10/11
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : vector_type
# @Software: PyCharm
from enum import StrEnum


class VectorType(StrEnum):
    PGVECTOR: str = "pgvector"
    QDRANT: str = "qdrant"
    CHROMA: str = "chroma"
