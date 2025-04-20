#!/usr/bin/env python3
"""
A utility to analyze a Python file and extract variables and functions in JSON format.
"""

import sys
import os
import ast
import json
from typing import Dict, List, Any, Optional, Union


# Ensure the output directory exists
def ensure_output_dir():
    """Create the output/code_analyzer directory if it doesn't exist."""
    output_dir = os.path.join("output", "code_analyzer")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return f"[bytes of length {len(o)}]"
        elif hasattr(o, "__dict__"):
            return o.__dict__
        try:
            return str(o)
        except:
            return f"[Object of type {type(o).__name__}]"


class CodeAnalyzer(ast.NodeVisitor):
    """
    AST visitor to extract variables and functions from Python code.
    """
    
    def __init__(self):
        self.variables = []
        self.functions = []
        self.classes = []
        self.current_scope = None
    
    def visit_Assign(self, node):
        """Extract variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Get variable value if it's a simple literal
                value = None
                if isinstance(node.value, ast.Constant):
                    value = node.value.value
                elif isinstance(node.value, ast.List):
                    value = "[list]"
                elif isinstance(node.value, ast.Dict):
                    value = "{dict}"
                elif isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        value = f"[result of {node.value.func.id}()]"
                    elif hasattr(node.value.func, 'attr'):
                        value = "[result of method call]"
                    else:
                        value = "[function call result]"
                else:
                    value = "[expression]"
                
                self.variables.append({
                    'name': target.id,
                    'line': node.lineno,
                    'value': value,
                    'scope': self.current_scope
                })
        
        # Continue exploring children
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Extract function definitions."""
        previous_scope = self.current_scope
        self.current_scope = node.name
        
        # Get parameters
        params = []
        for arg in node.args.args:
            param = {'name': arg.arg}
            # Get default value if available
            params.append(param)
        
        # Get docstring if available
        docstring = ast.get_docstring(node)
        
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'params': [arg.arg for arg in node.args.args],
            'docstring': docstring,
            'scope': previous_scope,
            'is_method': previous_scope is not None and previous_scope in [c['name'] for c in self.classes],
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
        })
        
        # Visit children
        self.generic_visit(node)
        self.current_scope = previous_scope
    
    def visit_ClassDef(self, node):
        """Extract class definitions."""
        previous_scope = self.current_scope
        self.current_scope = node.name
        
        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{self._get_attribute_full_name(base)}")
        
        # Get docstring if available
        docstring = ast.get_docstring(node)
        
        self.classes.append({
            'name': node.name,
            'line': node.lineno,
            'bases': bases,
            'docstring': docstring,
            'scope': previous_scope,
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
        })
        
        # Visit children
        self.generic_visit(node)
        self.current_scope = previous_scope
    
    def _get_decorator_name(self, decorator):
        """Extract the name of a decorator."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return self._get_attribute_full_name(decorator.func)
        elif isinstance(decorator, ast.Attribute):
            return self._get_attribute_full_name(decorator)
        return "[unknown]"
    
    def _get_attribute_full_name(self, node):
        """Get the full name of an attribute node."""
        if isinstance(node, ast.Attribute):
            return f"{self._get_attribute_full_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Name):
            return node.id
        return "[unknown]"


def analyze_file(file_path: str) -> Dict[str, Any]:
    """
    Analyze a Python file and return information about its structure.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        Dictionary containing extracted variables, functions, and classes
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Parse the AST
        tree = ast.parse(code, filename=file_path)
        
        # Analyze the code
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        
        # Get module docstring if available
        module_docstring = ast.get_docstring(tree)
        
        result = {
            "filename": os.path.basename(file_path),
            "path": file_path,
            "docstring": module_docstring,
            "variables": analyzer.variables,
            "functions": analyzer.functions,
            "classes": analyzer.classes
        }
        
        # Automatically save to JSON file in output directory
        output_dir = ensure_output_dir()
        output_filename = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_analysis.json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, cls=CustomJSONEncoder)
        
        return result
    except SyntaxError as e:
        error_result = {
            "error": f"Syntax error in file: {str(e)}",
            "filename": os.path.basename(file_path),
            "path": file_path
        }
        # Save error results to output directory
        output_dir = ensure_output_dir()
        output_filename = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_analysis_error.json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, indent=2, cls=CustomJSONEncoder)
        return error_result
    except Exception as e:
        error_result = {
            "error": f"Error analyzing file: {str(e)}",
            "filename": os.path.basename(file_path),
            "path": file_path
        }
        # Save error results to output directory
        output_dir = ensure_output_dir()
        output_filename = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_analysis_error.json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, indent=2, cls=CustomJSONEncoder)
        return error_result


def analyze_package(package_path: str, recursive: bool = True) -> Dict[str, Any]:
    """
    Analyze an entire Python package and return information about its structure.
    
    Args:
        package_path: Path to the Python package to analyze (directory with __init__.py)
        recursive: Whether to recursively analyze subpackages and modules
        
    Returns:
        Dictionary containing extracted variables, functions, and classes from all modules
    """
    if not os.path.isdir(package_path):
        return {"error": f"Not a directory: {package_path}"}
    
    # Check if this is a valid package (has __init__.py)
    init_file = os.path.join(package_path, "__init__.py")
    if not os.path.exists(init_file) and not os.path.exists(os.path.join(package_path, "__init__.pyc")):
        return {"error": f"Not a valid Python package (missing __init__.py): {package_path}"}
    
    package_name = os.path.basename(package_path)
    
    # Results will contain all package info
    results = {
        "package_name": package_name,
        "path": package_path,
        "modules": [],
        "subpackages": [],
        "all_variables": [],
        "all_functions": [],
        "all_classes": []
    }
    
    # Analyze __init__.py first
    init_analysis = analyze_file(init_file)
    if "error" not in init_analysis:
        results["modules"].append({
            "name": "__init__",
            "path": init_file,
            "analysis": init_analysis
        })
        results["all_variables"].extend(init_analysis["variables"])
        results["all_functions"].extend(init_analysis["functions"])
        results["all_classes"].extend(init_analysis["classes"])
    
    # Get all Python files and subpackages in this directory
    for item in os.listdir(package_path):
        item_path = os.path.join(package_path, item)
        
        # Skip __init__.py as we already analyzed it
        if item == "__init__.py":
            continue
        
        # Handle Python files
        if item.endswith(".py"):
            module_name = os.path.splitext(item)[0]
            module_analysis = analyze_file(item_path)
            
            if "error" not in module_analysis:
                results["modules"].append({
                    "name": module_name,
                    "path": item_path,
                    "analysis": module_analysis
                })
                
                # Add to combined results
                results["all_variables"].extend(module_analysis["variables"])
                results["all_functions"].extend(module_analysis["functions"])
                results["all_classes"].extend(module_analysis["classes"])
        
        # Handle subpackages if recursive
        elif os.path.isdir(item_path) and recursive:
            # Check if it's a package (has __init__.py)
            if os.path.exists(os.path.join(item_path, "__init__.py")):
                subpackage_analysis = analyze_package(item_path, recursive)
                
                if "error" not in subpackage_analysis:
                    results["subpackages"].append(subpackage_analysis)
                    
                    # Add to combined results
                    results["all_variables"].extend(subpackage_analysis["all_variables"])
                    results["all_functions"].extend(subpackage_analysis["all_functions"])
                    results["all_classes"].extend(subpackage_analysis["all_classes"])
    
    # Automatically save package analysis to a JSON file in output directory
    output_dir = ensure_output_dir()
    output_filename = os.path.join(output_dir, f"{package_name}_package_analysis.json")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=CustomJSONEncoder)
    
    return results


def analyze_module_by_name(module_name: str) -> Dict[str, Any]:
    """
    Analyze a Python module by its import name (e.g., 'os.path', 'numpy', etc.)
    
    Args:
        module_name: The name of the module as you would import it
        
    Returns:
        Dictionary containing extracted variables, functions, and classes
    """
    try:
        # Try to import the module
        import importlib
        module = importlib.import_module(module_name)
        
        # Get the file path
        if hasattr(module, "__file__") and module.__file__:
            module_path = module.__file__
            
            # Handle compiled modules (.pyc files)
            if module_path.endswith(".pyc") and not os.path.exists(module_path):
                module_path = module_path[:-1]  # Try .py instead
                
            # Handle packages
            if module_path.endswith("__init__.py"):
                package_dir = os.path.dirname(module_path)
                return analyze_package(package_dir)  # This now saves JSON automatically
            else:
                return analyze_file(module_path)  # This now saves JSON automatically
        else:
            # Built-in modules without a file
            result = {
                "module_name": module_name,
                "path": "built-in module",
                "variables": [],
                "functions": [],
                "classes": [],
                "error": "This is a built-in module without a Python source file."
            }
            
            # Save result to JSON file in output directory
            output_dir = ensure_output_dir()
            output_filename = os.path.join(output_dir, f"{module_name.replace('.', '_')}_module_analysis.json")
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, cls=CustomJSONEncoder)
                
            return result
    except ImportError as e:
        error_result = {
            "error": f"Could not import module {module_name}: {str(e)}"
        }
        
        # Save error to JSON file in output directory
        output_dir = ensure_output_dir()
        output_filename = os.path.join(output_dir, f"{module_name.replace('.', '_')}_module_error.json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, indent=2, cls=CustomJSONEncoder)
            
        return error_result
    except Exception as e:
        error_result = {
            "error": f"Error analyzing module {module_name}: {str(e)}"
        }
        
        # Save error to JSON file in output directory
        output_dir = ensure_output_dir()
        output_filename = os.path.join(output_dir, f"{module_name.replace('.', '_')}_module_error.json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, indent=2, cls=CustomJSONEncoder)
            
        return error_result


def get_analysis_json(analysis_result: Dict[str, Any], indent: int = 2) -> str:
    """
    Convert analysis result dictionary to formatted JSON string.
    
    Args:
        analysis_result: Result from analyze_file, analyze_package or analyze_module_by_name
        indent: Number of spaces for indentation in the JSON output
        
    Returns:
        Formatted JSON string representation of the analysis result
    """
    return json.dumps(analysis_result, indent=indent, cls=CustomJSONEncoder)


def save_analysis_to_file(analysis_result: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """
    Save analysis result to a file in JSON format.
    
    Args:
        analysis_result: Result from analyze_file, analyze_package or analyze_module_by_name
        file_path: Path to the output file
        indent: Number of spaces for indentation in the JSON output
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        # Use the CustomJSONEncoder
        json.dump(analysis_result, f, indent=indent, cls=CustomJSONEncoder)
    print(f"Analysis saved to {file_path}")


def main():
    """
    Main function to handle command line arguments and output results.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Python code structure and output in JSON format")
    parser.add_argument("target", help="Python file, package directory, or module name to analyze")
    parser.add_argument("-o", "--output", help="Output file to save results (if not specified, prints to stdout)")
    parser.add_argument("-m", "--module", action="store_true", help="Analyze a module by import name (e.g., 'os.path')")
    parser.add_argument("-p", "--package", action="store_true", help="Analyze a package directory")
    parser.add_argument("-r", "--no-recursive", action="store_true", help="Don't recursively analyze subpackages")
    
    args = parser.parse_args()
    
    # Determine what to analyze
    if args.module:
        # Analyze module by import name
        result = analyze_module_by_name(args.target)
    elif args.package:
        # Analyze package directory
        result = analyze_package(args.target, not args.no_recursive)
    else:
        # Default: analyze a file
        if os.path.isdir(args.target) and os.path.exists(os.path.join(args.target, "__init__.py")):
            # It's a package directory
            print(f"Detected a package directory. Analyzing as a package...")
            result = analyze_package(args.target, not args.no_recursive)
        else:
            # Regular file analysis
            result = analyze_file(args.target)
    
    # Output to file or stdout
    if args.output:
        # Check if output is a full path or just a filename
        if os.path.dirname(args.output):
            # It's a full path, use it as is
            output_path = args.output
        else:
            # Just a filename, put it in the output directory
            output_dir = ensure_output_dir()
            output_path = os.path.join(output_dir, args.output)
            
        save_analysis_to_file(result, output_path)
    else:
        # Print to stdout
        print(json.dumps(result, indent=2, cls=CustomJSONEncoder))


if __name__ == "__main__":
    main()
