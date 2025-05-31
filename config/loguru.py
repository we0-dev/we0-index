#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/07/17
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : loguru
# @Software: PyCharm
import inspect
import logging
import os
import sys
from typing import List, Dict

from loguru import logger

from constants.constants import Constants
from setting.setting import get_we0_index_settings
from utils.path_util import PathUtil

sider_settings = get_we0_index_settings()


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class Log:
    file_name = Constants.Common.PROJECT_NAME + '_{time}' + '.log'
    log_file_path = os.path.join(Constants.Path.LOG_PATH, file_name)
    logger_level = sider_settings.log.level
    logger_file = sider_settings.log.file
    DEFAULT_CONFIG = [
        {
            'sink': sys.stdout,
            'level': logger_level,
            'format': '[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>][<level>{level}</level>]'
                      '[<yellow>{file}</yellow>:<cyan>{line}</cyan>]: <level>{message}</level>',
            'colorize': True,  # 自定义配色
            'serialize': False,  # 序列化数据打印
            'backtrace': True,  # 是否显示完整的异常堆栈跟踪
            'diagnose': True,  # 异常跟踪是否显示触发异常的方法或语句所使用的变量，生产环境应设为 False
            'enqueue': False,  # 默认线程安全。若想实现协程安全 或 进程安全，该参数设为 True
            'catch': True,  # 捕获异常

        }
    ]
    if logger_file:
        DEFAULT_CONFIG.append({
            'sink': log_file_path,
            'level': logger_level,
            'format': '[{time:YYYY-MM-DD HH:mm:ss.SSS}][{level}][{file}:{line}]: {message}',
            'retention': '7 days',  # 日志保留时间
            'serialize': False,  # 序列化数据打印
            'backtrace': True,  # 是否显示完整的异常堆栈跟踪
            'diagnose': True,  # 异常跟踪是否显示触发异常的方法或语句所使用的变量，生产环境应设为 False
            'enqueue': False,  # 默认线程安全。若想实现协程安全 或 进程安全，该参数设为 True
            'catch': True,  # 捕获异常
        })

    @staticmethod
    def start(config: List[Dict] | None = None) -> None:
        PathUtil.check_or_make_dirs(
            Constants.Path.LOG_PATH
        )
        if config:
            logger.configure(handlers=config)
        else:
            logger.configure(handlers=Log.DEFAULT_CONFIG)
        if sider_settings.log.debug:
            logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        logger.enable('__main__')

    @staticmethod
    def close() -> None:
        logger.disable('__main__')
