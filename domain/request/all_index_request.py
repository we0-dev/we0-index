#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/23
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : all_index_request
# @Software: PyCharm
from pydantic import BaseModel, Field


class AllIndexRequest(BaseModel):
    repo_id: str = Field(description='仓库 ID')
