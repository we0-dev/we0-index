#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/23
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : delete_index_request
# @Software: PyCharm
from typing import List

from pydantic import BaseModel, Field


class DeleteIndexRequest(BaseModel):
    repo_id: str = Field(description='仓库 ID')
    file_id: List[str] = Field(description='仓库 ID')
