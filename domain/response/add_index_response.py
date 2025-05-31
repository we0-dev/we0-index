#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/23
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : add_index_response
# @Software: PyCharm
from typing import List

from pydantic import BaseModel


class FileInfoResponse(BaseModel):
    file_id: str
    relative_path: str


class AddIndexResponse(BaseModel):
    repo_id: str
    file_infos: List[FileInfoResponse]
