#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/23
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : retrieval_request
# @Software: PyCharm
from typing import List, Optional

from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    repo_id: str
    file_ids: Optional[List[str]] = None
    query: str
