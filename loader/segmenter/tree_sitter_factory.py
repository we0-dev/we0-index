#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/12
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : tree_sitter_factory
# @Software: PyCharm
from functools import lru_cache
from typing import Dict, Type, Set

from loader.segmenter.tree_sitter_segmenter import TreeSitterSegmenter


class TreeSitterFactory:
    __segmenter: Dict[str, Type[TreeSitterSegmenter]] = {}

    @classmethod
    def get_segmenter(cls, ext: str) -> Type[TreeSitterSegmenter]:
        if ext not in cls.__segmenter:
            raise ValueError(f'ext type {ext} is not supported')
        return cls.__segmenter[ext]

    @classmethod
    def __register(cls, ext: str, _cls: Type[TreeSitterSegmenter]):
        cls.__segmenter[ext] = _cls

    @classmethod
    def __has_cls(cls, ext: str) -> bool:
        return ext in cls.__segmenter

    @classmethod
    def register(
            cls,
            ext_set: Set[str]
    ):
        if not ext_set:
            raise ValueError('Must provide support extension set')

        def decorator(origin_cls):
            for ext in ext_set:
                if not cls.__has_cls(ext):
                    TreeSitterFactory.__register(ext, origin_cls)
            return origin_cls

        return decorator

    @classmethod
    @lru_cache
    def get_ext_set(cls) -> Set[str]:
        return set(cls.__segmenter.keys())
