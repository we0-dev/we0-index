from typing import List

from tree_sitter import Language

from loader.segmenter.tree_sitter_factory import TreeSitterFactory
from loader.segmenter.tree_sitter_segmenter import TreeSitterSegmenter


@TreeSitterFactory.register(ext_set={'.tsx'})
class TypeScriptXmlSegmenter(TreeSitterSegmenter):
    """Code segmenter for TypeScriptXml."""

    def get_language(self) -> Language:
        import tree_sitter_typescript
        return Language(tree_sitter_typescript.language_tsx())

    def get_node_types(self) -> List[str]:
        return [
            'lexical_declaration',
            'interface_declaration',
            'method_definition',
            'function_declaration',
            'export_statement'
        ]

    def get_recursion_node_types(self) -> List[str]:
        return [
            'class_declaration',
            'class_body'
        ]
