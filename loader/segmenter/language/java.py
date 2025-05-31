from typing import List

from tree_sitter import Language

from loader.segmenter.tree_sitter_factory import TreeSitterFactory
from loader.segmenter.tree_sitter_segmenter import TreeSitterSegmenter


@TreeSitterFactory.register(ext_set={'.java'})
class JavaSegmenter(TreeSitterSegmenter):
    """Code segmenter for Java."""

    def get_language(self) -> Language:
        import tree_sitter_java
        return Language(tree_sitter_java.language())

    def get_node_types(self) -> List[str]:
        return [
            'method_declaration',
            'enum_declaration'
        ]

    def get_recursion_node_types(self) -> List[str]:
        return [
            'class_declaration',
            'class_body',
            'interface_declaration',
            'interface_body'
        ]
