#!/usr/bin/env python3
"""Investigate typed parameter structure."""

import tree_sitter_python as ts_python
from tree_sitter import Language, Parser, Query, QueryCursor

PY_LANGUAGE = Language(ts_python.language())
parser = Parser(PY_LANGUAGE)

code = 'def foo(x: int, y: str = "default"): pass'

tree = parser.parse(bytes(code, "utf-8"))

def print_node(node, indent=0):
    text = code[node.start_byte:node.end_byte]
    if len(text) > 40:
        text = text[:40] + "..."
    print(f"{'  ' * indent}{node.type} = {text!r}")
    for child in node.children:
        print_node(child, indent + 1)

print("AST Structure:")
print_node(tree.root_node)

# Try different queries
print("\n\nTesting queries:")

queries = [
    ("parameters children", "(parameters (_) @param)"),
    ("typed_parameter exists?", "(typed_parameter) @tp"),
    ("function params", "(function_definition parameters: (parameters) @params)"),
    ("identifier with type", "(identifier) @id (type) @type"),
]

for name, q in queries:
    try:
        query = Query(PY_LANGUAGE, q)
        cursor = QueryCursor(query)
        caps = cursor.captures(tree.root_node)
        print(f"\n{name}: {list(caps.keys())}")
        for k, v in caps.items():
            for n in v[:2]:
                print(f"  @{k}: {code[n.start_byte:n.end_byte]!r}")
    except Exception as e:
        print(f"\n{name}: ERROR - {e}")
