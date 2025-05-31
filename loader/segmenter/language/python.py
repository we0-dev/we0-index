from typing import List

from tree_sitter import Language

from loader.segmenter.tree_sitter_factory import TreeSitterFactory
from loader.segmenter.tree_sitter_segmenter import TreeSitterSegmenter


@TreeSitterFactory.register(ext_set={'.py'})
class PythonSegmenter(TreeSitterSegmenter):
    """Code segmenter for Python."""

    def get_language(self) -> Language:
        import tree_sitter_python
        return Language(tree_sitter_python.language())

    def get_node_types(self) -> List[str]:
        return ['function_definition', 'decorated_definition']

    def get_recursion_node_types(self) -> List[str]:
        return ['class_definition', 'block']
