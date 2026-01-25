#!/usr/bin/env python3
"""Test script for py-tree-sitter Python parsing.

This script demonstrates:
- Parsing Python source code with tree-sitter
- Extracting function definitions with line numbers
- Extracting class definitions with their methods
- Extracting import statements
- Printing AST structure for a sample function
- Using TreeCursor for traversal
"""

import tree_sitter_python as ts_python
from tree_sitter import Language, Parser, Query, QueryCursor
from pathlib import Path


def create_parser():
    """Create and return a tree-sitter parser for Python."""
    PY_LANGUAGE = Language(ts_python.language())
    parser = Parser(PY_LANGUAGE)
    return parser, PY_LANGUAGE


def get_node_text(node, source_bytes=None):
    """Extract the text content of a node.

    Note: In tree-sitter 0.25+, nodes have a .text property that returns bytes.
    The source_bytes parameter is kept for backward compatibility but is optional.
    """
    # Use node.text property (returns bytes, decode to str)
    return node.text.decode('utf-8')


def extract_functions(tree, source_bytes):
    """Extract all function definitions with their line numbers."""
    functions = []

    def visit(node):
        if node.type == 'function_definition':
            # Get function name
            name_node = node.child_by_field_name('name')
            if name_node:
                name = get_node_text(name_node, source_bytes)
                # Line numbers are 0-indexed in tree-sitter, add 1 for human-readable
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1

                # Get parameters
                params_node = node.child_by_field_name('parameters')
                params = get_node_text(params_node, source_bytes) if params_node else "()"

                # Get return type annotation if present
                return_type = None
                return_node = node.child_by_field_name('return_type')
                if return_node:
                    return_type = get_node_text(return_node, source_bytes)

                functions.append({
                    'name': name,
                    'start_line': start_line,
                    'end_line': end_line,
                    'params': params,
                    'return_type': return_type,
                    'node': node  # Keep reference for later use
                })

        for child in node.children:
            visit(child)

    visit(tree.root_node)
    return functions


def extract_classes(tree, source_bytes):
    """Extract all class definitions with their methods."""
    classes = []

    def visit(node, parent_class=None):
        if node.type == 'class_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                class_name = get_node_text(name_node, source_bytes)
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1

                # Get base classes if any
                bases = []
                argument_list = node.child_by_field_name('superclasses')
                if argument_list:
                    for child in argument_list.children:
                        if child.type == 'identifier':
                            bases.append(get_node_text(child, source_bytes))

                # Get decorators
                decorators = []
                for child in node.children:
                    if child.type == 'decorator':
                        decorators.append(get_node_text(child, source_bytes))

                class_info = {
                    'name': class_name,
                    'start_line': start_line,
                    'end_line': end_line,
                    'bases': bases,
                    'decorators': decorators,
                    'methods': []
                }
                classes.append(class_info)

                # Find methods within this class
                body_node = node.child_by_field_name('body')
                if body_node:
                    for child in body_node.children:
                        if child.type == 'function_definition':
                            method_name_node = child.child_by_field_name('name')
                            if method_name_node:
                                method_name = get_node_text(method_name_node, source_bytes)
                                method_start = child.start_point[0] + 1
                                class_info['methods'].append({
                                    'name': method_name,
                                    'line': method_start
                                })

        for child in node.children:
            visit(child)

    visit(tree.root_node)
    return classes


def extract_imports(tree, source_bytes):
    """Extract all import statements."""
    imports = []

    def visit(node):
        if node.type == 'import_statement':
            imports.append({
                'type': 'import',
                'line': node.start_point[0] + 1,
                'text': get_node_text(node, source_bytes)
            })
        elif node.type == 'import_from_statement':
            imports.append({
                'type': 'from_import',
                'line': node.start_point[0] + 1,
                'text': get_node_text(node, source_bytes)
            })

        for child in node.children:
            visit(child)

    visit(tree.root_node)
    return imports


def print_ast_structure(node, source_bytes, indent=0, max_depth=5):
    """Print the AST structure for a node."""
    if indent > max_depth * 2:
        return

    prefix = "  " * indent
    node_text = get_node_text(node, source_bytes)

    # Truncate long text for display
    if len(node_text) > 50:
        node_text = node_text[:47] + "..."
    node_text = node_text.replace('\n', '\\n')

    # Show field name if this is a named field
    print(f"{prefix}{node.type} [{node.start_point[0]+1}:{node.start_point[1]}] = '{node_text}'")

    for child in node.children:
        print_ast_structure(child, source_bytes, indent + 1, max_depth)


def test_tree_cursor(tree, source_bytes):
    """Test TreeCursor traversal method."""
    cursor = tree.walk()

    print("\n" + "=" * 60)
    print("TreeCursor Traversal Test")
    print("=" * 60)

    # Depth-first traversal using cursor
    depth = 0
    visited = []

    def traverse():
        nonlocal depth
        node = cursor.node
        visited.append((depth, node.type, node.start_point[0] + 1))

        # Go to first child if exists
        if cursor.goto_first_child():
            depth += 1
            traverse()
            depth -= 1

            # Visit siblings
            while cursor.goto_next_sibling():
                traverse()

            cursor.goto_parent()

    traverse()

    # Print summary of traversal
    print(f"Total nodes visited: {len(visited)}")

    # Count node types
    node_types = {}
    for _, node_type, _ in visited:
        node_types[node_type] = node_types.get(node_type, 0) + 1

    print("\nNode type counts (top 10):")
    sorted_types = sorted(node_types.items(), key=lambda x: x[1], reverse=True)[:10]
    for node_type, count in sorted_types:
        print(f"  {node_type}: {count}")

    # Test cursor field access
    print("\nCursor field navigation test:")
    cursor = tree.walk()  # Reset cursor

    # Navigate to first function definition
    def find_first_function():
        if cursor.node.type == 'function_definition':
            return True
        if cursor.goto_first_child():
            if find_first_function():
                return True
            while cursor.goto_next_sibling():
                if find_first_function():
                    return True
            cursor.goto_parent()
        return False

    if find_first_function():
        func_node = cursor.node
        print(f"Found function: {get_node_text(func_node.child_by_field_name('name'), source_bytes)}")

        # Test cursor.field_name property
        cursor.goto_first_child()
        fields_found = []
        while True:
            field = cursor.field_name
            if field:
                fields_found.append((field, cursor.node.type))
            if not cursor.goto_next_sibling():
                break

        print(f"Fields in function node: {fields_found}")


def main():
    """Main test function."""
    # Setup
    script_dir = Path(__file__).parent
    sample_file = script_dir / "sample_python.py"

    print("=" * 60)
    print("Tree-sitter Python Parsing Test")
    print("=" * 60)

    # Create parser
    parser, language = create_parser()
    print(f"\nParser created successfully")
    print(f"Language: {language}")

    # Read source file
    source_code = sample_file.read_text()
    source_bytes = source_code.encode('utf-8')
    print(f"Source file: {sample_file}")
    print(f"Source length: {len(source_code)} characters")

    # Parse the code
    tree = parser.parse(source_bytes)
    print(f"\nParsing successful!")
    print(f"Root node type: {tree.root_node.type}")
    print(f"Root node children: {len(tree.root_node.children)}")

    # Extract and display functions
    print("\n" + "=" * 60)
    print("Function Definitions")
    print("=" * 60)
    functions = extract_functions(tree, source_bytes)
    for func in functions:
        return_type = f" -> {func['return_type']}" if func['return_type'] else ""
        print(f"  {func['name']}{func['params']}{return_type}")
        print(f"    Lines {func['start_line']}-{func['end_line']}")
    print(f"\nTotal functions found: {len(functions)}")

    # Extract and display classes
    print("\n" + "=" * 60)
    print("Class Definitions")
    print("=" * 60)
    classes = extract_classes(tree, source_bytes)
    for cls in classes:
        bases_str = f"({', '.join(cls['bases'])})" if cls['bases'] else ""
        decorators_str = ' '.join(cls['decorators']) + ' ' if cls['decorators'] else ""
        print(f"  {decorators_str}{cls['name']}{bases_str}")
        print(f"    Lines {cls['start_line']}-{cls['end_line']}")
        if cls['methods']:
            print(f"    Methods:")
            for method in cls['methods']:
                print(f"      - {method['name']} (line {method['line']})")
    print(f"\nTotal classes found: {len(classes)}")

    # Extract and display imports
    print("\n" + "=" * 60)
    print("Import Statements")
    print("=" * 60)
    imports = extract_imports(tree, source_bytes)
    for imp in imports:
        print(f"  Line {imp['line']}: {imp['text']}")
    print(f"\nTotal imports found: {len(imports)}")

    # Print AST structure for a sample function
    print("\n" + "=" * 60)
    print("AST Structure for 'simple_function'")
    print("=" * 60)
    for func in functions:
        if func['name'] == 'simple_function':
            print_ast_structure(func['node'], source_bytes, max_depth=4)
            break

    # Test TreeCursor traversal
    test_tree_cursor(tree, source_bytes)

    # Additional tests: Query API
    print("\n" + "=" * 60)
    print("Query API Test")
    print("=" * 60)

    # Create a query to find all function calls
    try:
        query_text = "(call function: (identifier) @func_name)"
        query = Query(language, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        print(f"Query: {query_text}")

        # captures returns a dict: {capture_name: [nodes]}
        func_nodes = captures.get('func_name', [])
        print(f"Function calls found: {len(func_nodes)}")

        # Group by function name
        call_counts = {}
        for node in func_nodes:
            func_name = node.text.decode('utf-8')
            call_counts[func_name] = call_counts.get(func_name, 0) + 1

        print("Function call counts:")
        for name, count in sorted(call_counts.items(), key=lambda x: -x[1]):
            print(f"  {name}: {count}")

    except Exception as e:
        print(f"Query API error: {e}")
        import traceback
        traceback.print_exc()

    # Test: Find all string literals
    print("\n" + "=" * 60)
    print("String Literals Query")
    print("=" * 60)
    try:
        query_text = "(string) @str"
        query = Query(language, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        str_nodes = captures.get('str', [])
        print(f"String literals found: {len(str_nodes)}")
        print("First 5 string literals:")
        for node in str_nodes[:5]:
            text = node.text.decode('utf-8')
            if len(text) > 60:
                text = text[:57] + "..."
            print(f"  Line {node.start_point[0]+1}: {text}")

    except Exception as e:
        print(f"Query API error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
