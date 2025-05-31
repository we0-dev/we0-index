#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/7/17
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : constants
# @Software: PyCharm
import os

from dotenv import find_dotenv, load_dotenv


class Constants:
    class Common:
        PROJECT_NAME: str = 'we0-index'

    class Path:
        # SYSTEM PATH
        ROOT_PATH: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        LOG_PATH: str = os.path.join(ROOT_PATH, 'log')
        RESOURCE_PATH: str = os.path.join(ROOT_PATH, 'resource')
        ENV_FILE_PATH: str = os.path.join(ROOT_PATH, '.env')
        TEMP_PATH: str = '/tmp'
        QDRANT_DEFAULT_DISK_PATH: str = os.path.join(ROOT_PATH, 'vector', 'qdrant')
        CHROMA_DEFAULT_DISK_PATH: str = os.path.join(ROOT_PATH, 'vector', 'chroma')

        # We0 CONFIG
        load_dotenv(ENV_FILE_PATH)
        YAML_FILE_PATH: str = find_dotenv(
            filename=os.path.join(
                RESOURCE_PATH,
                f"{os.environ.get('WE0_INDEX_ENV', 'dev')}.yaml"
            )
        )
