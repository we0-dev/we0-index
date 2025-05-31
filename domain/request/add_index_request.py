#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/23
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : add_index_request
# @Software: PyCharm
from typing import List

from pydantic import BaseModel, Field


class AddFileInfo(BaseModel):
    relative_path: str = Field(description='File Relative Path')
    content: str = Field(description='File Content')


class AddIndexRequest(BaseModel):
    uid: str = Field(description='Unique ID')
    repo_abs_path: str = Field(description='Repository Absolute Path')
    file_infos: List[AddFileInfo]
