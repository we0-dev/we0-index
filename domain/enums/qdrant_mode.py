#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/22
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : qdrant_mode
# @Software: PyCharm
from enum import StrEnum


class QdrantMode(StrEnum):
    DISK = "disk"
    REMOTE = "remote"
    MEMORY = "memory"
