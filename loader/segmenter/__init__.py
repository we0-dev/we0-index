#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/12
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : __init__.py
# @Software: PyCharm
from loader.segmenter.language.css import CssSegmenter
from loader.segmenter.language.go import GoSegmenter
from loader.segmenter.language.java import JavaSegmenter
from loader.segmenter.language.javascript import JavaScriptSegmenter
from loader.segmenter.language.python import PythonSegmenter
from loader.segmenter.language.typescript import TypeScriptSegmenter
from loader.segmenter.language.typescriptxml import TypeScriptXmlSegmenter

__all__ = [
    'CssSegmenter',
    'GoSegmenter',
    'JavaSegmenter',
    'JavaScriptSegmenter',
    'PythonSegmenter',
    'TypeScriptSegmenter',
    'TypeScriptXmlSegmenter'
]
