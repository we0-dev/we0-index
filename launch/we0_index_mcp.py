#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/6/2
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : we0_index_mcp
# @Software: PyCharm
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.tools import Tool
from mcp.server.lowlevel.server import LifespanResultT, Server
from mcp.shared.context import RequestT

from extensions import ext_manager
from router.git_router import clone_and_index
from router.vector_router import retrieval


@asynccontextmanager
async def lifespan(server: Server[LifespanResultT, RequestT]) -> AsyncIterator[object]:
    await ext_manager.init_vector()
    yield {}
    await ext_manager.init_vector()


def create_fast_mcp() -> FastMCP:
    app = FastMCP(
        name="We0 Index",
        description="CodeIndex, embedding, retrieval",
        tools=[
            Tool.from_function(clone_and_index),
            Tool.from_function(retrieval),
        ],
        lifespan=lifespan
    )
    return app


we0_index_mcp = create_fast_mcp()