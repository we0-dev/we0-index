#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/12
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : mimetype_util
# @Software: PyCharm
import mimetypes
import os


def guess_mimetype_and_extension(file_path: str) -> tuple[str | None, str | None]:
    """
    根据文件路径（通常是文件名或 URL 中的路径片段）来猜测 MIME 类型和扩展名。
    优先使用文件后缀名进行判断，如果没有后缀名则使用默认的 application/octet-stream。
    """
    _, extension = os.path.splitext(file_path)
    if extension:
        # 通过后缀名在 mimetypes 中查找 MIME 类型
        mimetype = mimetypes.types_map.get(extension.lower())
    else:
        # 如果没有扩展名，使用默认的二进制流类型
        mimetype = 'application/octet-stream'
        # 根据 MIME 类型再猜一次扩展名（一般会给出 .bin）
        extension = mimetypes.guess_extension(mimetype)

    return mimetype, extension
