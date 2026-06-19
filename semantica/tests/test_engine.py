import unittest
import ast
from src.analyzer import StructuralAnalyzer
from src.refactorer import AutonomousRefactorer

class TestSemanticaEngine(unittest.TestCase):

    def test_complex_nesting_is_decoupled(self):
        dirty_input = """
def process_data(items):
    for x in items:
        if x.is_valid:
            if x.value > 10:
                x.mark_verified()
"""
        tree = ast.parse(dirty_input)
        analyzer = StructuralAnalyzer()
        analyzer.visit(tree)
        
        refactorer = AutonomousRefactorer(analyzer.metrics, depth_threshold=3)
        modified_tree = refactorer.visit(tree)
        
        for helper in refactorer.extracted_functions:
            modified_tree.body.append(helper)
        ast.fix_missing_locations(modified_tree)
        
        final_code = ast.unparse(modified_tree)

        self.assertIn("_remediated_process_data_block", final_code)
        self.assertIn("def _remediated_process_data_block", final_code)

    def test_clean_code_remains_unchanged(self):
        clean_input = """
def shallow_function(x):
    if x > 5:
        return x * 2
    return x
"""
        tree = ast.parse(clean_input)
        analyzer = StructuralAnalyzer()
        analyzer.visit(tree)
        
        refactorer = AutonomousRefactorer(analyzer.metrics, depth_threshold=3)
        modified_tree = refactorer.visit(tree)
        final_code = ast.unparse(modified_tree)

        self.assertEqual(len(refactorer.extracted_functions), 0)

if __name__ == "__main__":
    unittest.main()