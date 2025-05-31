#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/23
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : ext_manager
# @Software: PyCharm
from loguru import logger

from extensions.vector.ext_vector import Vector


class ExtManager:
    vector = Vector()


async def init_vector():
    logger.info("Initializing vector")
    await ExtManager.vector.init_app()
    logger.info("Initialized vector")
