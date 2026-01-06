"""
Script to generate metainfo.txt for Quantlet based on Python file contents.
Analyzes a .py file and creates structured metadata following Quantlet standards.
"""

import os
import re
import ast
from datetime import datetime
from pathlib import Path


def extract_docstring(file_path):
    """Extract module-level docstring from Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            return ast.get_docstring(tree) or ""
    except Exception as e:
        print(f"Error parsing docstring: {e}")
        return ""


def extract_imports(file_path):
    """Extract all import statements from Python file."""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
    except Exception as e:
        print(f"Error extracting imports: {e}")
    return sorted(imports)


def extract_functions(file_path):
    """Extract function names from Python file."""
    functions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Skip private functions
                        functions.append(node.name)
    except Exception as e:
        print(f"Error extracting functions: {e}")
    return functions


def extract_keywords_from_content(file_path, docstring, imports):
    """Generate keywords based on file content, docstring, and imports."""
    keywords = set()

    # Add keywords from imports
    keyword_mapping = {
        'pandas': 'data analysis',
        'numpy': 'numerical computation',
        'matplotlib': 'visualization',
        'seaborn': 'visualization',
        'scipy': 'scientific computing',
        'statsmodels': 'statistics',
        'sklearn': 'machine learning',
        'tensorflow': 'deep learning',
        'torch': 'deep learning',
        'requests': 'web scraping',
        'beautifulsoup4': 'web scraping',
        'sqlalchemy': 'database',
        'sqlite3': 'database',
        'psycopg2': 'database'
    }

    for imp in imports:
        if imp in keyword_mapping:
            keywords.add(keyword_mapping[imp])

    # Extract keywords from docstring
    doc_lower = docstring.lower()
    keyword_terms = [
        'regression', 'classification', 'clustering', 'time series',
        'forecast', 'prediction', 'optimization', 'simulation',
        'portfolio', 'risk', 'volatility', 'return', 'finance',
        'statistics', 'econometrics', 'quantile', 'distribution'
    ]

    for term in keyword_terms:
        if term in doc_lower:
            keywords.add(term)

    return sorted(keywords)


def generate_metainfo(py_file_path, author="", output_path=None):
    """
    Generate metainfo.txt file based on Python file contents.

    Parameters:
    -----------
    py_file_path : str
        Path to the Python file to analyze
    author : str
        Author name (optional)
    output_path : str
        Path where metainfo.txt should be saved (default: same directory as py file)
    """
    py_file_path = Path(py_file_path)

    if not py_file_path.exists():
        print(f"Error: File {py_file_path} does not exist")
        return

    if not py_file_path.suffix == '.py':
        print("Error: File must be a Python (.py) file")
        return

    # Extract information
    quantlet_name = py_file_path.stem
    docstring = extract_docstring(py_file_path)
    imports = extract_imports(py_file_path)
    functions = extract_functions(py_file_path)
    keywords = extract_keywords_from_content(py_file_path, docstring, imports)

    # Prepare description
    description = docstring.split('\n')[0] if docstring else "Python script for quantitative analysis"

    # Prepare output path
    if output_path is None:
        output_path = py_file_path.parent / "metainfo.txt"
    else:
        output_path = Path(output_path)

    # Generate metainfo content
    metainfo_content = f"""Name of Quantlet: {quantlet_name}

Published in: 'Quantlet Research'

Description: '{description}'

Keywords: {', '.join(keywords) if keywords else 'python, quantitative analysis'}

Author: {author if author else '[Author Name]'}

Submitted: {datetime.now().strftime('%a, %B %d %Y')}

Datafile: ''

Example:
"""

    # Add function information if available
    if functions:
        metainfo_content += f"\nMain Functions:\n"
        for func in functions:
            metainfo_content += f"- {func}\n"

    # Add package dependencies
    if imports:
        metainfo_content += f"\nPackage Dependencies:\n"
        for imp in imports:
            metainfo_content += f"- {imp}\n"

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(metainfo_content)

    print(f"metainfo.txt created successfully at: {output_path}")
    print(f"\nSummary:")
    print(f"  Quantlet Name: {quantlet_name}")
    print(f"  Functions Found: {len(functions)}")
    print(f"  Imports Found: {len(imports)}")
    print(f"  Keywords: {len(keywords)}")


def main():
    """Main function to run the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate metainfo.txt for Quantlet based on Python file contents'
    )
    parser.add_argument(
        'py_file',
        help='Path to the Python file to analyze'
    )
    parser.add_argument(
        '--author',
        default='',
        help='Author name for the metainfo file'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output path for metainfo.txt (default: same directory as input file)'
    )

    args = parser.parse_args()

    generate_metainfo(args.py_file, args.author, args.output)


if __name__ == "__main__":
    main()
