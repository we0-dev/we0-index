#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/18
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : helper
# @Software: PyCharm

import uuid
from hashlib import sha256
from typing import Optional, Literal, Union, Collection

import tiktoken


class Helper:
    # 缓存字典，用于存储生成的编码器实例
    _encoders_cache = {}

    @staticmethod
    def generate_text_hash(text: str) -> str:
        """生成文本的SHA-256哈希值"""
        return sha256(text.encode()).hexdigest()

    @staticmethod
    def calculate_tokens(
            text: str,
            encoding_name: str = "cl100k_base",
            model_name: Optional[str] = None,
            allowed_special=None,
            disallowed_special: Union[Literal["all"], Collection[str]] = "all",
    ) -> int:
        """使用tiktoken编码器计算文本的token数量"""
        if allowed_special is None:
            allowed_special = set()

        # 使用model_name/encoding_name和特殊字符集合作为缓存键
        cache_key = (model_name, encoding_name, frozenset(allowed_special), disallowed_special)

        # 如果缓存中已有相应的编码器实例，则直接返回
        if cache_key in Helper._encoders_cache:
            return Helper._encoders_cache[cache_key](text)

        # 根据模型名或编码名称来选择合适的编码器
        if model_name:
            enc = tiktoken.encoding_for_model(model_name)
        else:
            enc = tiktoken.get_encoding(encoding_name)

        # 创建新的编码器
        def _tiktoken_encoder(_text: str) -> int:
            """计算给定文本的token数量"""
            return len(
                enc.encode(
                    _text,
                    allowed_special=allowed_special,
                    disallowed_special=disallowed_special,
                )
            )

        # 缓存编码器并返回计算结果
        Helper._encoders_cache[cache_key] = _tiktoken_encoder
        return _tiktoken_encoder(text)

    @staticmethod
    def generate_fixed_uuid(unique_str: str) -> str:
        namespace = uuid.NAMESPACE_URL
        return str(uuid.uuid5(namespace, unique_str))
