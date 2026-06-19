import ast

class AutonomousRefactorer(ast.NodeTransformer):
    """Safely extracts complex, deeply nested blocks into standalone decoupled components."""
    
    def __init__(self, metrics, depth_threshold=3):
        super().__init__()
        self.metrics = metrics
        self.depth_threshold = depth_threshold
        self.extracted_functions = []

    def visit_FunctionDef(self, node):
        # Recursively visit child nodes first to ensure inner scopes are processed
        self.generic_visit(node)
        
        # Retrieve computed structural metrics for this specific function
        function_metric = self.metrics.get(node.name)
        if not function_metric or function_metric["max_nesting_depth"] < self.depth_threshold:
            return node

        # Iterate through target complex structural blocks identified during analysis
        for block_info in function_metric["blocks"]:
            target_block = block_info["node"]
            
            # Ensure the target structural node is an immediate child of the function body
            if target_block in node.body:
                idx = node.body.index(target_block)
                helper_name = f"_remediated_{node.name}_block"
                
                inputs = block_info["inputs"]
                outputs = block_info["outputs"]

                # 1. Construct the arguments list for the new decoupled helper function
                new_args = ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=var) for var in inputs],
                    kwonlyargs=[], 
                    kwdefaults=[], 
                    defaults=[]
                )
                
                # 2. Build the body of the new function out of the complex block
                new_body = [target_block]
                
                # If variables were mutated inside the block, return them to preserve scope state
                if outputs:
                    if len(outputs) == 1:
                        return_val = ast.Name(id=outputs[0], ctx=ast.Load())
                    else:
                        return_val = ast.Tuple(elts=[ast.Name(id=o, ctx=ast.Load()) for o in outputs], ctx=ast.Load())
                    new_body.append(ast.Return(value=return_val))

                # Create the standalone FunctionDef node
                extracted_func = ast.FunctionDef(
                    name=helper_name,
                    args=new_args,
                    body=new_body,
                    decorator_list=[]
                )
                self.extracted_functions.append(extracted_func)

                # 3. Build the call expression to replace the messy block in the original function
                call_args = [ast.Name(id=var, ctx=ast.Load()) for var in inputs]
                engine_call = ast.Call(
                    func=ast.Name(id=helper_name, ctx=ast.Load()),
                    args=call_args,
                    keywords=[]
                )

                # Assign the returned values back to local variables if mutations occurred
                if outputs:
                    if len(outputs) == 1:
                        target_assign = ast.Name(id=outputs[0], ctx=ast.Store())
                    else:
                        target_assign = ast.Tuple(elts=[ast.Name(id=o, ctx=ast.Store()) for o in outputs], ctx=ast.Store())
                    
                    replacement_node = ast.Assign(targets=[target_assign], value=engine_call)
                else:
                    replacement_node = ast.Expr(value=engine_call)

                # Execute the live AST node replacement mutation swap
                node.body[idx] = replacement_node
                break

        return node