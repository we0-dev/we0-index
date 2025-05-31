#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/22
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : retrieval_segment_response
# @Software: PyCharm
from pydantic import BaseModel, Field, ConfigDict


class RetrievalSegmentResponse(BaseModel):
    relative_path: str = Field(description='代码段所属文件相对路径')
    start_line: int = Field(description='代码段开始行')
    end_line: int = Field(description='代码段结束行')
    score: float = Field(description='相似度评分')
    model_config = ConfigDict(
        extra='ignore'
    )
