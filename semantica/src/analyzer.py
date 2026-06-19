import ast

class ScopeFinder(ast.NodeVisitor):
    """Analyzes a specific sub-tree to find read (inputs) and written (outputs) variables."""
    def __init__(self):
        self.read_vars = set()
        self.written_vars = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.written_vars.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.read_vars.add(node.id)
        self.generic_visit(node)


class StructuralAnalyzer(ast.NodeVisitor):
    """Tracks metrics like nesting depth across loops, try-except blocks, and comprehensions."""
    def __init__(self):
        self.current_depth = 0
        self.max_depth = 0
        self.metrics = {}

    def visit_FunctionDef(self, node):
        old_max = self.max_depth
        self.max_depth = 0
        self.current_depth = 0
        
        self.generic_visit(node)
        
        blocks_to_analyze = []
        # Expand tracking to include structural Try statements
        for child in node.body:
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                scope = ScopeFinder()
                scope.visit(child)
                blocks_to_analyze.append({
                    "node": child,
                    "inputs": sorted(list(scope.read_vars - scope.written_vars)),
                    "outputs": sorted(list(scope.written_vars))
                })

        self.metrics[node.name] = {
            "max_nesting_depth": self.max_depth,
            "blocks": blocks_to_analyze
        }
        self.max_depth = old_max

    def _visit_control_flow(self, node):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth
        self.generic_visit(node)
        self.current_depth -= 1

    # Native AST hooks for loops and conditions
    visit_If = _visit_control_flow
    visit_For = _visit_control_flow
    visit_While = _visit_control_flow
    
    # Advanced targets: capture try blocks and nested generator metrics
    visit_Try = _visit_control_flow
    visit_ListComp = _visit_control_flow