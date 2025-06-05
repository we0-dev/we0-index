#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/7/29
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : launch
# @Software: PyCharm
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config.loguru import Log
from domain.result.result import Result
from exception.exception import CommonException
from extensions import ext_manager
from router.git_router import git_router
from router.vector_router import vector_router
from setting.setting import get_we0_index_settings

settings = get_we0_index_settings()


async def initialize_extensions():
    await asyncio.gather(
        ext_manager.init_vector(),
    )


async def close_extensions():
    ...


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    try:
        Log.start()
        await initialize_extensions()
        yield
    finally:
        await close_extensions()
        Log.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="We0 Index",
        description="We0 Index API",
        version="0.1.0",
        lifespan=lifespan
    )

    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()
# 注册路由
app.include_router(vector_router, prefix="/vector", tags=["vector"])
app.include_router(git_router, prefix="/git", tags=["git"])


@app.exception_handler(CommonException)
async def common_exception_handler(request: Request, exc: CommonException):
    error = Result.failed(code=-1, message=exc.message)
    logger.exception(f"Url: {request.url}, Exception: CommonException, Error: {error}")
    return JSONResponse(content=jsonable_encoder(error))


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    error = Result.failed(code=-1, message=str(exc.args))
    logger.exception(f"Url: {request.url}, {type(exc).__name__}: {exc} , Error: {error}")
    return JSONResponse(content=jsonable_encoder(error))


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
