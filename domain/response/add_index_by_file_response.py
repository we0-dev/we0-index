#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/23
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : add_index_by_file_response
# @Software: PyCharm

from pydantic import BaseModel


class AddIndexByFileResponse(BaseModel):
    repo_id: str
    file_id: str
