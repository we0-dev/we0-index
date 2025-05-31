from typing import List

from tree_sitter import Language

from loader.segmenter.tree_sitter_factory import TreeSitterFactory
from loader.segmenter.tree_sitter_segmenter import TreeSitterSegmenter


@TreeSitterFactory.register(ext_set={'.go'})
class GoSegmenter(TreeSitterSegmenter):
    """Code segmenter for Go."""

    def get_language(self) -> Language:
        import tree_sitter_go
        return Language(tree_sitter_go.language())

    def get_node_types(self) -> List[str]:
        return [
            'method_declaration',
            'function_declaration',
            'type_declaration'
        ]

    def get_recursion_node_types(self) -> List[str]:
        return []
