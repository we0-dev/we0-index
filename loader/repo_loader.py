#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/10/11
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : repo_loader
# @Software: PyCharm
"""Abstract interface for document loader implementations."""

from typing import AsyncIterator, Type

from domain.entity.blob import Blob
from domain.entity.code_segment import CodeSegment
from loader.segmenter.base_line_segmenter import LineBasedSegmenter
from loader.segmenter.base_segmenter import BaseSegmenter
from loader.segmenter.tree_sitter_factory import TreeSitterFactory


class RepoLoader:

    @classmethod
    def get_segmenter_constructor(cls, extension: str | None = None) -> Type[BaseSegmenter]:
        if extension in TreeSitterFactory.get_ext_set():
            return TreeSitterFactory.get_segmenter(extension)
        else:
            return LineBasedSegmenter

    @classmethod
    async def load_blob(cls, blob: Blob) -> AsyncIterator[CodeSegment]:
        try:
            text = await blob.as_string()
        except Exception as e:
            raise e

        segmenter = cls.get_segmenter_constructor(extension=blob.extension).from_tiktoken_encoder(text=text)
        if not segmenter.is_valid():
            segmenter = cls.get_segmenter_constructor().from_tiktoken_encoder(text=text)

        for code in segmenter.segment():
            yield code
