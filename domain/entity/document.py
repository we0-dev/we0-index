#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/14
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : document
# @Software: PyCharm
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentMeta(BaseModel):
    repo_id: Optional[str] = Field(description='仓库ID')
    file_id: Optional[str] = Field(description='文件ID')
    segment_id: str = Field(description='代码段ID uuid4')
    relative_path: str = Field(description='代码段所属文件相对路径')
    start_line: int = Field(description='代码块启始行')
    end_line: int = Field(description='代码块结束行')
    segment_block: int = Field(description='代码块序号')
    segment_hash: str = Field(description='代码段哈希')
    segment_cl100k_base_token: Optional[int] = Field(default=None, description='代码段 cl100k_base token')
    segment_o200k_base_token: Optional[int] = Field(default=None, description='代码段 o200k_base token')
    description: Optional[str] = Field(default=None, description='代码描述 可选 用于描述嵌入')

    score: Optional[float] = Field(default=None, description='相似度评分 仅在相似度匹配时使用')
    content: Optional[str] = Field(default=None, description='代码块纯文本 兼容qdrant，qdrant其他字段只能存储在payload')

    model_config = ConfigDict(
        extra='ignore'
    )


class Document(BaseModel):
    vector: List[float] = Field(description='向量Embedding', default_factory=list)
    content: Optional[str] = Field(default=None, description='纯文本代码')
    meta: Optional[DocumentMeta] = Field(default=None, description='代码元数据')

    model_config = ConfigDict(
        extra='ignore'
    )
