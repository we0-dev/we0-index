#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/15
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : model_provider
# @Software: PyCharm
from enum import StrEnum


class ModelType(StrEnum):
    OPENAI = "openai"
    JINA = "jina"
