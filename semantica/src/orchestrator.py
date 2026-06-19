import os
import sys
import ast
import argparse
import difflib  # Built-in library to generate standard diffs

from analyzer import StructuralAnalyzer
from refactorer import AutonomousRefactorer

def generate_diff(original_source: str, remediated_source: str, file_path: str) -> str:
    """Generates a clean unified diff context string between original and new code."""
    original_lines = original_source.splitlines(keepends=True)
    remediated_lines = remediated_source.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        remediated_lines,
        fromfile=f"a/{file_path} (Original)",
        tofile=f"b/{file_path} (Remediated)"
    )
    return "".join(diff)

def remediate_file(file_path: str, dry_run: bool = False):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"[\033[91mError\033[0m] Failed to parse syntax for {file_path}: {e}")
        return

    # Phase 1: Structural Context Capture
    analyzer = StructuralAnalyzer()
    analyzer.visit(tree)

    # Phase 2: Autonomous Code Mutation
    refactorer = AutonomousRefactorer(analyzer.metrics, depth_threshold=3)
    modified_tree = refactorer.visit(tree)

    if refactorer.extracted_functions:
        for helper in refactorer.extracted_functions:
            modified_tree.body.append(helper)
        
        ast.fix_missing_locations(modified_tree)
        remediated_source = ast.unparse(modified_tree)
        
        if dry_run:
            print(f"\n--- [\033[94mDry-Run Preview\033[0m] Changes for {file_path} ---")
            diff_output = generate_diff(source, remediated_source, file_path)
            
            # Print with subtle ANSI color terminal formatting for clarity
            for line in diff_output.splitlines():
                if line.startswith('+') and not line.startswith('+++'):
                    print(f"\033[92m{line}\033[0m")  # Green for additions
                elif line.startswith('-') and not line.startswith('---'):
                    print(f"\033[91m{line}\033[0m")  # Red for deletions
                else:
                    print(line)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(remediated_source)
            print(f"[\033[92mSuccess\033[0m] Remediated and saved: {file_path}")
    else:
        if not dry_run:
            print(f"[\033[90mPass\033[0m] {file_path} conforms to safe complexity baselines.")

def main():
    parser = argparse.ArgumentParser(description="Semantica: Autonomous Code Remediation Engine")
    parser.add_argument("target", help="Directory path containing target python files to process")
    parser.add_argument("--dry-run", action="store_true", help="Preview architectural remediations without saving changes")
    
    args = parser.parse_args()
    target_dir = args.target
    
    if not os.path.exists(target_dir):
        print(f"[\033[91mError\033[0m] Target directory '{target_dir}' not found.")
        sys.exit(1)

    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                remediate_file(os.path.join(root, file), dry_run=args.dry_run)

if __name__ == "__main__":
    main()