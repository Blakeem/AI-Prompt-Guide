#!/usr/bin/env python3
"""
Test script for tree-sitter TypeScript parsing.
Extracts functions, classes, interfaces, types, exports, and imports.
"""

import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Parser
from pathlib import Path
from typing import Any


def setup_parser() -> Parser:
    """Initialize the TypeScript parser."""
    TS_LANGUAGE = Language(ts_typescript.language_typescript())
    parser = Parser(TS_LANGUAGE)
    return parser


def get_node_text(node: Any, source_code: bytes) -> str:
    """Extract text from a node."""
    return source_code[node.start_byte:node.end_byte].decode('utf-8')


def find_nodes_by_type(node: Any, node_types: list[str]) -> list[Any]:
    """Recursively find all nodes of specified types."""
    results = []

    if node.type in node_types:
        results.append(node)

    for child in node.children:
        results.extend(find_nodes_by_type(child, node_types))

    return results


def extract_imports(tree: Any, source_code: bytes) -> list[dict]:
    """Extract all import statements."""
    imports = []
    import_nodes = find_nodes_by_type(tree.root_node, ['import_statement'])

    for node in import_nodes:
        import_info = {
            'type': 'import',
            'text': get_node_text(node, source_code),
            'line': node.start_point[0] + 1,
        }

        # Find the source module
        for child in node.children:
            if child.type == 'string':
                import_info['source'] = get_node_text(child, source_code).strip('"\'')
            elif child.type == 'import_clause':
                import_info['clause'] = get_node_text(child, source_code)

        imports.append(import_info)

    return imports


def extract_interfaces(tree: Any, source_code: bytes) -> list[dict]:
    """Extract all interface declarations."""
    interfaces = []
    interface_nodes = find_nodes_by_type(tree.root_node, ['interface_declaration'])

    for node in interface_nodes:
        interface_info = {
            'type': 'interface',
            'line': node.start_point[0] + 1,
            'properties': [],
            'is_exported': False,
        }

        # Check parent for export
        parent = node.parent
        if parent and parent.type == 'export_statement':
            interface_info['is_exported'] = True

        for child in node.children:
            if child.type == 'type_identifier':
                interface_info['name'] = get_node_text(child, source_code)
            elif child.type == 'interface_body':
                # Extract property signatures from interface_body
                for prop in child.children:
                    if prop.type == 'property_signature':
                        prop_text = get_node_text(prop, source_code)
                        interface_info['properties'].append(prop_text.strip())

        interfaces.append(interface_info)

    return interfaces


def extract_types(tree: Any, source_code: bytes) -> list[dict]:
    """Extract all type alias declarations."""
    types = []
    type_nodes = find_nodes_by_type(tree.root_node, ['type_alias_declaration'])

    for node in type_nodes:
        type_info = {
            'type': 'type_alias',
            'line': node.start_point[0] + 1,
            'text': get_node_text(node, source_code),
        }

        for child in node.children:
            if child.type == 'type_identifier':
                type_info['name'] = get_node_text(child, source_code)

        types.append(type_info)

    return types


def extract_functions(tree: Any, source_code: bytes) -> list[dict]:
    """Extract all function declarations (regular and arrow)."""
    functions = []

    # Regular function declarations
    func_nodes = find_nodes_by_type(tree.root_node, ['function_declaration'])
    for node in func_nodes:
        func_info = {
            'type': 'function_declaration',
            'line': node.start_point[0] + 1,
            'is_async': False,
            'is_exported': False,
        }

        # Check parent for export
        parent = node.parent
        if parent and parent.type == 'export_statement':
            func_info['is_exported'] = True

        for child in node.children:
            if child.type == 'identifier':
                func_info['name'] = get_node_text(child, source_code)
            elif child.type == 'formal_parameters':
                func_info['parameters'] = get_node_text(child, source_code)
            elif child.type == 'type_annotation':
                func_info['return_type'] = get_node_text(child, source_code)
            elif child.type == 'async':
                func_info['is_async'] = True

        functions.append(func_info)

    # Arrow functions (lexical declarations with arrow function expressions)
    lexical_decls = find_nodes_by_type(tree.root_node, ['lexical_declaration'])
    for node in lexical_decls:
        # Check if this contains an arrow function
        arrow_nodes = find_nodes_by_type(node, ['arrow_function'])
        if arrow_nodes:
            arrow_func = arrow_nodes[0]
            func_info = {
                'type': 'arrow_function',
                'line': node.start_point[0] + 1,
                'is_async': False,
                'is_exported': False,
            }

            # Check parent for export
            parent = node.parent
            if parent and parent.type == 'export_statement':
                func_info['is_exported'] = True

            # Find variable name
            for child in node.children:
                if child.type == 'variable_declarator':
                    for var_child in child.children:
                        if var_child.type == 'identifier':
                            func_info['name'] = get_node_text(var_child, source_code)

            # Get arrow function details
            for child in arrow_func.children:
                if child.type == 'formal_parameters':
                    func_info['parameters'] = get_node_text(child, source_code)
                elif child.type == 'type_annotation':
                    func_info['return_type'] = get_node_text(child, source_code)

            functions.append(func_info)

    return functions


def extract_classes(tree: Any, source_code: bytes) -> list[dict]:
    """Extract all class declarations with their methods."""
    classes = []
    class_nodes = find_nodes_by_type(tree.root_node, ['class_declaration'])

    for node in class_nodes:
        class_info = {
            'type': 'class',
            'line': node.start_point[0] + 1,
            'methods': [],
            'properties': [],
            'is_exported': False,
            'extends': None,
        }

        # Check parent for export
        parent = node.parent
        if parent and parent.type == 'export_statement':
            class_info['is_exported'] = True

        for child in node.children:
            if child.type == 'type_identifier':
                class_info['name'] = get_node_text(child, source_code)
            elif child.type == 'class_heritage':
                # Extract extends clause
                for heritage_child in child.children:
                    if heritage_child.type == 'extends_clause':
                        for ext_child in heritage_child.children:
                            if ext_child.type == 'identifier':
                                class_info['extends'] = get_node_text(ext_child, source_code)
            elif child.type == 'class_body':
                # Extract methods and properties
                for body_child in child.children:
                    if body_child.type == 'method_definition':
                        method_info = extract_method_info(body_child, source_code)
                        class_info['methods'].append(method_info)
                    elif body_child.type == 'public_field_definition':
                        prop_text = get_node_text(body_child, source_code)
                        class_info['properties'].append(prop_text.strip())

        classes.append(class_info)

    return classes


def extract_method_info(node: Any, source_code: bytes) -> dict:
    """Extract method information from a method_definition node."""
    method_info = {
        'name': '',
        'visibility': 'public',
        'is_static': False,
        'is_async': False,
        'line': node.start_point[0] + 1,
    }

    for child in node.children:
        if child.type == 'property_identifier':
            method_info['name'] = get_node_text(child, source_code)
        elif child.type == 'accessibility_modifier':
            method_info['visibility'] = get_node_text(child, source_code)
        elif child.type == 'formal_parameters':
            method_info['parameters'] = get_node_text(child, source_code)
        elif child.type == 'type_annotation':
            method_info['return_type'] = get_node_text(child, source_code)
        elif child.type == 'static':
            method_info['is_static'] = True
        elif child.type == 'async':
            method_info['is_async'] = True

    return method_info


def extract_exports(tree: Any, source_code: bytes) -> list[dict]:
    """Extract all export statements."""
    exports = []
    export_nodes = find_nodes_by_type(tree.root_node, ['export_statement'])

    for node in export_nodes:
        export_info = {
            'type': 'export',
            'line': node.start_point[0] + 1,
            'is_default': False,
            'exported_items': [],
        }

        # Check what's being exported
        for child in node.children:
            if child.type == 'default':
                export_info['is_default'] = True
            elif child.type == 'function_declaration':
                for func_child in child.children:
                    if func_child.type == 'identifier':
                        export_info['exported_items'].append({
                            'kind': 'function',
                            'name': get_node_text(func_child, source_code)
                        })
                        break
            elif child.type == 'class_declaration':
                for class_child in child.children:
                    if class_child.type == 'type_identifier':
                        export_info['exported_items'].append({
                            'kind': 'class',
                            'name': get_node_text(class_child, source_code)
                        })
                        break
            elif child.type == 'lexical_declaration':
                for var_child in child.children:
                    if var_child.type == 'variable_declarator':
                        for id_child in var_child.children:
                            if id_child.type == 'identifier':
                                export_info['exported_items'].append({
                                    'kind': 'const',
                                    'name': get_node_text(id_child, source_code)
                                })
                                break
            elif child.type == 'interface_declaration':
                for int_child in child.children:
                    if int_child.type == 'type_identifier':
                        export_info['exported_items'].append({
                            'kind': 'interface',
                            'name': get_node_text(int_child, source_code)
                        })
                        break

        exports.append(export_info)

    return exports


def print_section(title: str, items: list[dict]) -> None:
    """Print a section with formatted items."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

    if not items:
        print("  (none found)")
        return

    for item in items:
        print(f"\n  Line {item.get('line', '?')}:")
        for key, value in item.items():
            if key != 'line':
                if isinstance(value, list):
                    print(f"    {key}:")
                    for v in value:
                        print(f"      - {v}")
                else:
                    print(f"    {key}: {value}")


def main():
    """Main entry point."""
    # Setup
    parser = setup_parser()

    # Read the TypeScript file
    sample_file = Path("/home/blake/Development/AI-Prompt-Guide/tree-sitter-tests/sample_typescript.ts")

    if not sample_file.exists():
        print(f"Error: Sample file not found at {sample_file}")
        return

    source_code = sample_file.read_bytes()

    # Parse
    print(f"Parsing: {sample_file}")
    print(f"File size: {len(source_code)} bytes")

    tree = parser.parse(source_code)

    print(f"Root node type: {tree.root_node.type}")
    print(f"Has errors: {tree.root_node.has_error}")

    # Extract all components
    imports = extract_imports(tree, source_code)
    interfaces = extract_interfaces(tree, source_code)
    types = extract_types(tree, source_code)
    functions = extract_functions(tree, source_code)
    classes = extract_classes(tree, source_code)
    exports = extract_exports(tree, source_code)

    # Print results
    print_section("IMPORTS", imports)
    print_section("INTERFACES", interfaces)
    print_section("TYPE ALIASES", types)
    print_section("FUNCTIONS (Regular + Arrow)", functions)
    print_section("CLASSES", classes)
    print_section("EXPORTS", exports)

    # Summary
    print(f"\n{'='*60}")
    print(" SUMMARY")
    print('='*60)
    print(f"  Imports:    {len(imports)}")
    print(f"  Interfaces: {len(interfaces)}")
    print(f"  Types:      {len(types)}")
    print(f"  Functions:  {len(functions)}")
    print(f"  Classes:    {len(classes)}")
    print(f"  Exports:    {len(exports)}")

    # Count exported items
    exported_funcs = sum(1 for f in functions if f.get('is_exported'))
    exported_classes = sum(1 for c in classes if c.get('is_exported'))
    print(f"\n  Exported functions: {exported_funcs}")
    print(f"  Exported classes:   {exported_classes}")

    # List all node types at top level for reference
    print(f"\n{'='*60}")
    print(" TOP-LEVEL NODE TYPES")
    print('='*60)
    for child in tree.root_node.children:
        if child.type not in ['comment']:
            print(f"  {child.type} (line {child.start_point[0] + 1})")


if __name__ == "__main__":
    main()
