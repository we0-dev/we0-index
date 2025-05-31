#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/8/21
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : exception
# @Software: PyCharm


class CommonException(Exception):
    def __init__(self, message=''):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class StorageUploadFileException(CommonException):
    ...
