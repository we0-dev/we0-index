from typing import List

from tree_sitter import Language

from loader.segmenter.tree_sitter_factory import TreeSitterFactory
from loader.segmenter.tree_sitter_segmenter import TreeSitterSegmenter


@TreeSitterFactory.register(ext_set={'.css'})
class CssSegmenter(TreeSitterSegmenter):
    """Code segmenter for Css."""

    def get_language(self) -> Language:
        import tree_sitter_css
        return Language(tree_sitter_css.language())

    def get_node_types(self) -> List[str]:
        return [
            'rule_set',
            'keyframes_statement',
            'media_statement'
        ]

    def get_recursion_node_types(self) -> List[str]:
        return []
