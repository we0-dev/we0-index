#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/7/18
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : path_util
# @Software: PyCharm
import os


class PathUtil:
    @staticmethod
    def check_or_make_dir(path: str):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def check_or_make_dirs(*paths):
        for path in paths:
            PathUtil.check_or_make_dir(path)
