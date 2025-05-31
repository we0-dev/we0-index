#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/11
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : line_based_segmenter
# @Software: PyCharm
from bisect import bisect_right, bisect_left
from typing import List, Dict, Any, Tuple, Iterator

from domain.entity.code_segment import CodeSegment
from loader.segmenter.base_segmenter import BaseSegmenter


class LineBasedSegmenter(BaseSegmenter):

    def __init__(
            self,
            text: str,
            max_chunk_size: int = 50,
            min_chunk_size: int = 10,
            delimiters=None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.delimiters = delimiters or ['\n\n', '\n']

        # 构建行号位置映射
        self.line_positions = self._build_line_positions(text)

    def segment(self) -> Iterator[CodeSegment]:
        """执行分块操作"""
        initial_range = (0, len(self.text))
        segments = self._recursive_split(initial_range, self.delimiters)
        if self.merge_small_chunks:
            segments = self._merge_small_segments(segments)
        for segment in segments:
            code_segment = CodeSegment.model_validate(segment)
            if not code_segment.code.isspace():
                yield code_segment

    @staticmethod
    def _build_line_positions(text: str) -> List[Tuple[int, int]]:
        """生成每行的字符位置范围列表 (start, end)"""
        lines = []
        start = 0
        for line in text.split('\n'):
            end = start + len(line)
            lines.append((start, end))
            start = end + 1  # 跳过换行符
        return lines

    def _get_original_lines(self, start_pos: int, end_pos: int) -> Tuple[int, int]:
        """根据字符位置获取原始行号 (1-based)"""
        starts = [line[0] for line in self.line_positions]
        ends = [line[1] for line in self.line_positions]

        start_line = bisect_right(starts, start_pos)
        end_line = bisect_left(ends, end_pos)

        # 处理边界情况
        start_line = max(0, start_line - 1) if start_line > 0 else 0
        end_line = min(end_line, len(ends) - 1)

        return start_line + 1, end_line + 1  # 转换为1-based

    def _recursive_split(
            self,
            char_range: Tuple[int, int],
            delimiters: List[str]
    ) -> List[Dict[str, Any]]:
        start_pos, end_pos = char_range
        text = self.text[start_pos:end_pos]

        if self.max_tokens is not None:
            raw_lines = text.splitlines(keepends=True)
            segments = []
            current_chunk_start = start_pos
            pos = start_pos
            any_long_line = False
            for line in raw_lines:
                # 对单行去掉首尾空白后计算 token 数
                if self.length_function(line.strip()) > self.max_tokens:
                    any_long_line = True
                    # 先处理该行之前的部分（如果存在）
                    if pos > current_chunk_start:
                        segments.extend(
                            self._recursive_split((current_chunk_start, pos), delimiters)
                        )
                    # 对这一行进行强制拆分（标记 forced 为 True）
                    segments.extend(
                        self._forced_split((pos, pos + len(line)), block=1)
                    )
                    current_chunk_start = pos + len(line)
                pos += len(line)
            if any_long_line:
                if current_chunk_start < end_pos:
                    segments.extend(
                        self._recursive_split((current_chunk_start, end_pos), delimiters)
                    )
                return segments

        current_lines = len(text.splitlines())

        # 判断是否需要分割
        need_split = False
        if current_lines > self.max_chunk_size:
            need_split = True
        if self.max_tokens is not None:
            current_tokens = self.length_function(text)
            if current_tokens > self.max_tokens:
                need_split = True

        if not need_split:
            code = text.strip()
            if not code:
                return []
            start_line, end_line = self._get_original_lines(start_pos, end_pos)
            # 正常返回的分块，标记 forced 为 False
            return [{
                "start": start_line,
                "end": end_line,
                "code": code,
                "forced": False
            }]

        # 尝试使用当前分隔符分割
        if delimiters:
            current_delim = delimiters[0]
            parts = text.split(current_delim)
            if len(parts) > 1:
                return self._split_by_delimiter(start_pos, end_pos, current_delim, delimiters[1:])

        # 无有效分隔符时强制分割
        return self._forced_split(char_range)

    def _split_by_delimiter(
            self,
            start_pos: int,
            end_pos: int,
            delimiter: str,
            next_delimiters: List[str]
    ) -> List[Dict[str, Any]]:
        """使用指定分隔符进行分割"""
        text = self.text[start_pos:end_pos]
        delim_len = len(delimiter)
        segments = []
        current_start = start_pos

        for part in text.split(delimiter):
            if not part.strip():
                current_start += len(part) + delim_len
                continue

            part_end = current_start + len(part)
            sub_segments = self._recursive_split(
                (current_start, part_end),
                next_delimiters
            )
            segments.extend(sub_segments)
            current_start = part_end + delim_len

        return segments

    def _compute_optimal_chunk_length(self, char_range: Tuple[int, int]) -> int:
        """
        在指定的字符区间内（二分查找），计算一个合适的拆分长度，使得：
        self.length_function(文本[start_pos:start_pos+chunk_len]) <= self.max_tokens
        """
        start_pos, end_pos = char_range
        total_chars = end_pos - start_pos

        low, high = 1, total_chars
        increment_value = self.max_tokens // 10
        optimal = low  # 至少保证 1 个字符
        while low <= high:
            mid = (low + high) // 2
            chunk_text = self.text[start_pos:start_pos + mid]
            token_count = self.length_function(chunk_text)
            if token_count <= self.max_tokens:
                # 当前长度符合要求，记录下来并尝试更大的长度
                optimal = mid
                low = mid + increment_value
            else:
                # 当前长度超出限制，尝试减小长度
                high = mid - increment_value

        return optimal

    def _forced_split(self, char_range: Tuple[int, int], block: int = 1) -> List[Dict[str, Any]]:
        start_pos, end_pos = char_range
        segments = []
        pos = start_pos
        current_block = block

        while pos < end_pos:
            optimal_chunk_size = self._compute_optimal_chunk_length((pos, end_pos))
            next_pos = min(pos + optimal_chunk_size, end_pos)
            chunk_text = self.text[pos:next_pos].strip()
            if chunk_text:
                start_line, end_line = self._get_original_lines(pos, next_pos)
                segments.append({
                    "start": start_line,
                    "end": end_line,
                    "code": chunk_text,
                    "forced": True,  # 标记为强制拆分生成的片段
                    "block": current_block
                })
                current_block += 1
            pos = next_pos
        return segments

    def _merge_small_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        merged = []
        if not segments:
            return merged
        buffer = segments[0]
        for seg in segments[1:]:
            # 如果一个分块是强制拆分的，而另一个不是，则不进行合并，直接分开处理
            if buffer.get("forced", False) != seg.get("forced", False):
                merged.append(buffer)
                buffer = seg
                continue

            merged_code = f"{buffer['code']}\n{seg['code']}"
            merged_lines = len(merged_code.splitlines())
            current_lines = buffer["end"] - buffer["start"] + 1
            next_lines = seg["end"] - seg["start"] + 1

            if self.max_tokens is not None:
                # 有 token 限制时，必须确保合并后 token 数不超过限制
                merged_tokens = self.length_function(merged_code)
                if merged_tokens <= self.max_tokens:
                    buffer = {
                        "start": buffer["start"],
                        "end": seg["end"],
                        "code": merged_code.strip(),
                        "forced": buffer.get("forced", False)
                    }
                else:
                    merged.append(buffer)
                    buffer = seg
            else:
                # 无 token 限制时，基于行数进行合并：
                # 如果合并后行数不超过 max_chunk_size 或者任一块过小，都可以合并
                if (merged_lines <= self.max_chunk_size) or (
                        current_lines < self.min_chunk_size or next_lines < self.min_chunk_size):
                    buffer = {
                        "start": buffer["start"],
                        "end": seg["end"],
                        "code": merged_code.strip(),
                        "forced": buffer.get("forced", False)
                    }
                else:
                    merged.append(buffer)
                    buffer = seg
        merged.append(buffer)
        return merged
