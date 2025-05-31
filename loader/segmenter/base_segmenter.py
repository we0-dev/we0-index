#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/12
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : base_segmenter
# @Software: PyCharm
from abc import ABC, abstractmethod
from typing import Any, Callable, Collection, Union, Literal, Optional, Iterator

from domain.entity.code_segment import CodeSegment


class BaseSegmenter(ABC):
    def __init__(
            self,
            max_tokens: int = 512,
            length_function: Callable[[str], int] = len,
            merge_small_chunks: bool = False,
    ):
        self.max_tokens = max_tokens
        self.length_function = length_function
        self.merge_small_chunks = merge_small_chunks

    def is_valid(self) -> bool:
        return True

    @abstractmethod
    def segment(self) -> Iterator[CodeSegment]:
        raise NotImplementedError

    @classmethod
    def from_huggingface_tokenizer(cls, tokenizer: Any, **kwargs: Any):
        """Text splitter that uses HuggingFace tokenizer to count length."""
        try:
            from transformers import PreTrainedTokenizerBase

            if not isinstance(tokenizer, PreTrainedTokenizerBase):
                raise ValueError(
                    "Tokenizer received was not an instance of PreTrainedTokenizerBase"
                )

            def _huggingface_tokenizer_length(text: str) -> int:
                return len(tokenizer.encode(text))

        except ImportError:
            raise ValueError(
                "Could not import transformers python package. "
                "Please install it with `pip install transformers`."
            )
        return cls(length_function=_huggingface_tokenizer_length, **kwargs)

    @classmethod
    def from_tiktoken_encoder(
            cls,
            encoding_name: str = "cl100k_base",
            model_name: Optional[str] = None,
            allowed_special=None,
            disallowed_special: Union[Literal["all"], Collection[str]] = "all",
            **kwargs: Any,
    ):
        """Text splitter that uses tiktoken encoder to count length."""
        if allowed_special is None:
            allowed_special = set()
        import tiktoken
        if model_name:
            enc = tiktoken.encoding_for_model(model_name)
        else:
            enc = tiktoken.get_encoding(encoding_name)

        def _tiktoken_encoder(text: str) -> int:
            return len(
                enc.encode(
                    text,
                    allowed_special=allowed_special,
                    disallowed_special=disallowed_special,
                )
            )

        return cls(length_function=_tiktoken_encoder, **kwargs)
