#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/10/12
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : task_context
# @Software: PyCharm

from pydantic import BaseModel, ConfigDict

from domain.entity.blob import Blob


class TaskContext(BaseModel):
    repo_id: str
    file_id: str
    relative_path: str
    blob: Blob
    model_config = ConfigDict(extra='ignore')
