from typing import List

from tree_sitter import Language

from loader.segmenter.tree_sitter_factory import TreeSitterFactory
from loader.segmenter.tree_sitter_segmenter import TreeSitterSegmenter


@TreeSitterFactory.register(ext_set={'.js', '.mjs'})
class JavaScriptSegmenter(TreeSitterSegmenter):
    """Code segmenter for JavaScript."""

    def get_language(self) -> Language:
        import tree_sitter_javascript
        return Language(tree_sitter_javascript.language())

    def get_node_types(self) -> List[str]:
        return [
            'lexical_declaration',
            'interface_declaration',
            'export_statement',
            'method_definition',
            'function_declaration',
            'function_expression',
            'generator_function',
            'generator_function_declaration'
        ]

    def get_recursion_node_types(self) -> List[str]:
        return [
            'class_declaration',
            'class_body'
        ]
