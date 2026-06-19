import os
import sys
import ast
from analyzer import StructuralAnalyzer
from refactorer import AutonomousRefactorer

def remediate_file(file_path: str):
    print(f"[Semantica Engine] Processing: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"[Error] Failed to parse syntax for {file_path}: {e}")
        return

    analyzer = StructuralAnalyzer()
    analyzer.visit(tree)

    refactorer = AutonomousRefactorer(analyzer.metrics, depth_threshold=3)
    modified_tree = refactorer.visit(tree)

    if refactorer.extracted_functions:
        for helper in refactorer.extracted_functions:
            modified_tree.body.append(helper)
        
        ast.fix_missing_locations(modified_tree)
        remediated_source = ast.unparse(modified_tree)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(remediated_source)
        print(f"[Success] Remediated and saved: {file_path}")
    else:
        print(f"[Pass] {file_path} conforms to safe complexity baselines.")

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "/app/target"
    
    if not os.path.exists(target_dir):
        print(f"[Error] Target workspace path directory '{target_dir}' not found.")
        sys.exit(1)

    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                remediate_file(os.path.join(root, file))

if __name__ == "__main__":
    main()