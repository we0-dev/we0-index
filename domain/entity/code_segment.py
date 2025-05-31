#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/17
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : code_segment
# @Software: PyCharm
from pydantic import BaseModel, ConfigDict, Field


class CodeSegment(BaseModel):
    start: int
    end: int
    code: str
    block: int = Field(default=1)
    model_config = ConfigDict(
        extra='ignore'
    )
