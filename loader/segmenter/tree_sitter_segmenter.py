from abc import abstractmethod
from collections import deque
from typing import List, Dict, Any, Iterator

from tree_sitter import Language, Parser

from domain.entity.code_segment import CodeSegment
from loader.segmenter.base_segmenter import BaseSegmenter


class TreeSitterSegmenter(BaseSegmenter):
    def __init__(
            self,
            text: str,
            chunk_size: int = 30,
            min_chunk_size: int = 10,
            max_chunk_size: int = 50,
            max_depth: int = 5,
            split_large_chunks=True,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text
        self.chunk_size = chunk_size
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.max_depth = max_depth
        self.split_large_chunks = split_large_chunks
        self.parser = self.get_parser()

    @abstractmethod
    def get_language(self) -> Language:
        """返回 Tree-sitter 对应语言对象。示例:
        return Language('build/my-languages.so', 'python')
        """
        raise NotImplementedError

    @abstractmethod
    def get_node_types(self) -> List[str]:
        """
        返回要提取的“目标节点类型”，
        如 ["function_definition", "class_definition"] 等
        """
        raise NotImplementedError

    @abstractmethod
    def get_recursion_node_types(self) -> List[str]:
        """
        返回需要继续递归遍历其子节点的类型，
        如 ["module", "block", "class_definition", "function_definition"] 等
        """
        raise NotImplementedError

    def is_valid(self) -> bool:
        """简单检查语法是否存在 ERROR 节点"""
        error_query = self.parser.language.query("(ERROR) @error")
        tree = self.parser.parse(bytes(self.text, encoding="UTF-8"))
        return len(error_query.captures(tree.root_node)) == 0

    def segment(self) -> Iterator[CodeSegment]:
        tree = self.parser.parse(bytes(self.text, "utf-8"))
        unfiltered_nodes = deque()
        for child in tree.root_node.children:
            unfiltered_nodes.append((child, 1))
        all_nodes = []
        while unfiltered_nodes:
            current_node, current_depth = unfiltered_nodes.popleft()
            if current_node.type in self.get_node_types():
                all_nodes.append(current_node)
            if current_node.type in self.get_recursion_node_types():
                if current_depth < self.max_depth:
                    for child in current_node.children:
                        unfiltered_nodes.append((child, current_depth + 1))
        all_nodes.sort(key=lambda n: (n.start_point[0], -n.end_point[0]))

        processed_ranges = []
        processed_chunks_info = []
        for node in all_nodes:
            start_0 = node.start_point[0]
            end_0 = node.end_point[0]
            node_text = node.text.decode()
            if self._is_range_covered(start_0, end_0, processed_ranges):
                continue
            processed_ranges.append((start_0, end_0))
            processed_chunks_info.append({
                "start": start_0 + 1,
                "end": end_0 + 1,
                "code": node_text
            })

        processed_chunks_info.sort(key=lambda x: x["start"])
        # 用 split("\n") 来和 Tree-sitter 的行数计算方式保持一致
        code_lines = self.text.split("\n")
        # 明确计算总行数：tree-sitter 的行数 = 文件中 "\n" 数量 + 1
        total_lines = self.text.count("\n") + 1

        combined_chunks = []
        current_pos = 0  # 0-based 行号
        for chunk in processed_chunks_info:
            chunk_start_0 = chunk["start"] - 1
            chunk_end_0 = chunk["end"] - 1
            if current_pos < chunk_start_0:
                unprocessed = self._handle_unprocessed(
                    code_lines[current_pos:chunk_start_0],
                    current_pos
                )
                combined_chunks.extend(unprocessed)
            combined_chunks.append({
                "start": chunk["start"],
                "end": chunk["end"],
                "code": chunk["code"]
            })
            current_pos = chunk_end_0 + 1

        if current_pos < total_lines:
            unprocessed = self._handle_unprocessed(
                code_lines[current_pos:total_lines],
                current_pos
            )
            combined_chunks.extend(unprocessed)

        final_chunks = self._post_process_chunks(combined_chunks)
        if self.max_tokens:
            final_chunks = self._split_by_tokens(final_chunks, self.max_tokens)
        for segment in final_chunks:
            code_segment = CodeSegment.model_validate(segment)
            if not code_segment.code.isspace():
                yield code_segment

    def get_parser(self) -> Parser:
        """初始化并返回 Parser 对象"""
        parser = Parser()
        parser.language = self.get_language()
        return parser

    @staticmethod
    def _is_range_covered(start: int, end: int, existing_ranges: List[tuple]) -> bool:
        """
        优化后的区间覆盖检查（时间复杂度 O(n)）。
        如果已有区间 [existing_start, existing_end] 能完全覆盖 [start, end]，则返回 True
        """
        for (existing_start, existing_end) in existing_ranges:
            if existing_start <= start and end <= existing_end:
                return True
        return False

    def _handle_unprocessed(self, lines: List[str], start_0: int) -> List[Dict[str, Any]]:
        """处理未识别的代码区域。"""
        if not lines:
            return []
        return self._split_into_chunks_without_empty_lines(lines, start_0)

    @staticmethod
    def _split_into_chunks_without_empty_lines(
            lines: List[str],
            start_0_based: int
    ) -> List[Dict[str, Any]]:
        """将未识别区域当作一个连续块输出，保留所有行"""
        return [{
            "start": start_0_based + 1,
            "end": start_0_based + len(lines),
            "code": "\n".join(lines)
        }]

    def _post_process_chunks(
            self,
            chunks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        对 chunks 做二次处理：
        1) 如果 chunk 行数 > max_chunk_size，按 chunk_size 均分拆分（行数维度）。
        2) 如果 chunk 行数 < min_chunk_size，尝试与前或后合并（只要合并后不超过 max_chunk_size）。
        """
        # 第一步：先将所有大于 max_chunk_size 的 chunk 拆分
        split_chunks = []
        if self.split_large_chunks:
            for c in chunks:
                if len(c['code']):
                    split_chunks.extend(
                        self._split_large_chunk(c, self.chunk_size, self.max_chunk_size)
                    )
        else:
            split_chunks = chunks

        # 第二步：对拆分后的结果，进行“过短合并”
        if self.merge_small_chunks:
            return self._merge_small_chunks(
                split_chunks,
                self.min_chunk_size,
                self.max_chunk_size,
                self.chunk_size
            )
        else:
            return split_chunks

    @staticmethod
    def _split_large_chunk(
            chunk: Dict[str, Any],
            chunk_size: int,
            max_chunk_size: int
    ) -> List[Dict[str, Any]]:
        """
        如果某个 chunk 行数大于 max_chunk_size，
        则根据 chunk_size 进行“均分拆分”，保证子块不会过大或过小。
        """
        lines = chunk["code"].split("\n")
        total_lines = len(lines)
        if total_lines <= max_chunk_size:
            return [chunk]

        # 初步估计拆分为 n 块
        n = max(1, round(total_lines / chunk_size))
        # 如果拆分后每块依旧大于 max_chunk_size，则增加 n
        while (total_lines / n) > max_chunk_size:
            n += 1
        # 确保 n 不超过 total_lines
        n = min(n, total_lines)

        base_size = total_lines // n
        remainder = total_lines % n  # 前 remainder 块每块多 1 行
        results = []
        current_index = 0
        original_start = chunk["start"]
        for i in range(n):
            current_chunk_size = base_size + (1 if i < remainder else 0)
            sub_lines = lines[current_index: current_index + current_chunk_size]
            results.append({
                "start": original_start + current_index,
                "end": original_start + current_index + current_chunk_size - 1,
                "code": "\n".join(sub_lines)
            })
            current_index += current_chunk_size
        return results

    @staticmethod
    def _merge_small_chunks(
            chunks: List[Dict[str, Any]],
            min_chunk_size: int,
            max_chunk_size: int,
            chunk_size: int
    ) -> List[Dict[str, Any]]:
        """
        对较小 chunk (< min_chunk_size) 做前后合并（只要合并后不超过 max_chunk_size）。
        同时设置了一个“理想范围”容差（tolerance_low ~ tolerance_high），
        如果相邻块本身已经在理想范围内，就不再合并以免破坏合理块。
        """
        merged = chunks.copy()
        changed = True
        tolerance_low = 0.8 * chunk_size
        tolerance_high = 1.2 * chunk_size

        while changed:
            changed = False
            new_merged = []
            i = 0
            while i < len(merged):
                current = merged[i]
                current_lines = len(current["code"].split("\n"))

                # 如果当前 chunk 已经足够大，则直接放入 new_merged
                if current_lines >= min_chunk_size:
                    new_merged.append(current)
                    i += 1
                    continue

                best_merge = None
                best_score = float('inf')

                # 尝试与前一个合并
                if new_merged:
                    prev = new_merged[-1]
                    prev_lines = len(prev["code"].split("\n"))
                    # 如果前一个 chunk 不在理想范围内，且合并后行数不超过 max_chunk_size
                    if not (tolerance_low <= prev_lines <= tolerance_high):
                        if prev_lines + current_lines <= max_chunk_size:
                            score = abs((prev_lines + current_lines) - chunk_size)
                            if score < best_score:
                                best_merge = 'prev'
                                best_score = score
                # 尝试与后一个合并
                if i + 1 < len(merged):
                    nxt = merged[i + 1]
                    nxt_lines = len(nxt["code"].split("\n"))
                    if not (tolerance_low <= nxt_lines <= tolerance_high):
                        if current_lines + nxt_lines <= max_chunk_size:
                            score = abs((current_lines + nxt_lines) - chunk_size)
                            if score < best_score:
                                best_merge = 'next'
                if best_merge == 'prev':
                    prev = new_merged.pop()
                    new_chunk = {
                        "start": prev["start"],
                        "end": current["end"],
                        "code": prev["code"] + "\n" + current["code"]
                    }
                    new_merged.append(new_chunk)
                    i += 1
                    changed = True
                elif best_merge == 'next':
                    nxt = merged[i + 1]
                    new_chunk = {
                        "start": current["start"],
                        "end": nxt["end"],
                        "code": current["code"] + "\n" + nxt["code"]
                    }
                    new_merged.append(new_chunk)
                    i += 2
                    changed = True
                else:
                    # 如果当前 chunk 特别小 (< min_chunk_size/2)，则尝试强制与前一个合并
                    if current_lines < (min_chunk_size / 2) and new_merged:
                        prev = new_merged.pop()
                        new_chunk = {
                            "start": prev["start"],
                            "end": current["end"],
                            "code": prev["code"] + "\n" + current["code"]
                        }
                        new_merged.append(new_chunk)
                        changed = True
                    else:
                        new_merged.append(current)
                    i += 1
            merged = new_merged
        return merged

    def _split_by_tokens(
            self,
            chunks: List[Dict[str, Any]],
            max_tokens: int,
            block: int = 1
    ) -> List[Dict[str, Any]]:
        processed = []
        for chunk in chunks:
            current_code = chunk["code"]
            current_tokens = self.length_function(current_code)
            if current_tokens <= max_tokens:
                if block == 1:
                    processed.append(chunk)
                else:
                    # 为分割后的块添加序号标记
                    chunk_with_part = chunk.copy()
                    chunk_with_part["block"] = block
                    processed.append(chunk_with_part)
                continue

            lines = current_code.split('\n')
            if len(lines) > 1:
                split_index = len(lines) // 2
                first_code = '\n'.join(lines[:split_index])
                second_code = '\n'.join(lines[split_index:])
                first_start = chunk["start"]
                first_end = first_start + split_index - 1
                second_start = first_end + 1
                second_end = chunk["end"]
                first_sub = {"start": first_start, "end": first_end, "code": first_code}
                second_sub = {"start": second_start, "end": second_end, "code": second_code}
                processed.extend(self._split_by_tokens([first_sub, second_sub], max_tokens, block))
            else:
                code = current_code
                low, high = 0, len(code)
                best_mid = 0
                while low <= high:
                    mid = (low + high) // 2
                    part = code[:mid]
                    if self.length_function(part) <= max_tokens:
                        best_mid = mid
                        low = mid + 1
                    else:
                        high = mid - 1
                best_mid = best_mid if best_mid != 0 else len(code) // 2
                first_part = code[:best_mid]
                second_part = code[best_mid:]
                first_sub = {"start": chunk["start"], "end": chunk["end"], "code": first_part}
                second_sub = {"start": chunk["start"], "end": chunk["end"], "code": second_part}
                # 递归调用时增加序号
                processed.extend(self._split_by_tokens([first_sub], max_tokens, block))
                processed.extend(self._split_by_tokens([second_sub], max_tokens, block + 1))
        return processed
