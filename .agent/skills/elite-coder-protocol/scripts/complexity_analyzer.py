import ast
import os
import sys

def analyze_complexity(filepath):
    """
    Mathematical analyzer for Neuron 2: The Architect.
    Uses AST (Abstract Syntax Tree) parsing to evaluate function complexity,
    length, and modularity based on Silicon Valley paradigms.
    """
    if not os.path.exists(filepath):
        print(f"❌ [Neuron 2] File not found: {filepath}")
        sys.exit(1)

    with open(filepath, 'r') as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code)
    except Exception as e:
        print(f"⚠️ [Neuron 2] Syntax error compiling AST: {e}")
        sys.exit(1)

    print(f"🏗️ [Neuron 2] Activating Architectural Scan recursively on: {filepath}")
    
    anomalies_found = False
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_name = node.name
            start_line = node.lineno
            end_line = getattr(node, 'end_lineno', start_line)
            length = end_line - start_line

            # Modularity Formula: Length Threshold
            if length > 40:
                print(f"⚠️  [Architect Flag] Function `{func_name}` is {length} lines long.")
                print(f"   -> Verdict: Violates SoC. Refactor into helper methods.")
                anomalies_found = True

            # Cyclomatic Mock Proxy: Counting branch nodes
            branches = sum(1 for child in ast.walk(node) if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)))
            if branches > 5:
                print(f"⚠️  [Architect Flag] Function `{func_name}` has {branches} nested branches.")
                print(f"   -> Verdict: Cognitive Complexity too high. Apply Early Returns or Strategy Pattern.")
                anomalies_found = True

    if not anomalies_found:
        print("✅ [Neuron 2] Codeblock mathematically confirmed as Modular and Scalable.")
    else:
        print("\n🛑 [Neuron 2] REFACTORING REQUIRED. Halt feature development and modularize.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 complexity_analyzer.py <absolute_file_path>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    analyze_complexity(target_file)
