# py-tree-sitter: Comprehensive Reference Guide

## Overview

py-tree-sitter is a Python binding for the Tree-sitter parsing library. It parses source code into a Concrete Syntax Tree (CST) - a structured, queryable representation of code syntax. It supports 30+ programming languages through a unified API.

**Key Strengths:**
- Extremely fast parsing (sub-millisecond for most files)
- Incremental parsing (only re-parse changed portions)
- Error-tolerant (produces valid trees even with syntax errors)
- Unified API across all languages
- Powerful query language for pattern matching
- Works on partial/incomplete code

---

## Installation

```bash
# Option 1: Pre-built language bindings (easiest)
pip install tree-sitter-languages

# Option 2: Core library + individual language packages
pip install tree-sitter
pip install tree-sitter-python tree-sitter-javascript tree-sitter-typescript
# etc.
```

**Available via tree-sitter-languages:**
Python, JavaScript, TypeScript, Go, Rust, C, C++, Java, Ruby, PHP, C#, Kotlin, Scala, Swift, Bash, JSON, YAML, TOML, HTML, CSS, SQL, Regex, and more.

---

## Basic Usage

### Parsing Code

```python
from tree_sitter_languages import get_language, get_parser

# Get parser for a language
parser = get_parser('python')
language = get_language('python')

# Parse source code (must be bytes)
code = b"""
def greet(name):
    print(f"Hello, {name}!")

class Person:
    def __init__(self, name):
        self.name = name
    
    def say_hello(self):
        greet(self.name)
"""

tree = parser.parse(code)
root = tree.root_node
```

### Parsing Files

```python
def parse_file(filepath: str, language: str):
    parser = get_parser(language)
    with open(filepath, 'rb') as f:
        code = f.read()
    return parser.parse(code), code
```

---

## Node Properties

Every node in the tree has these properties:

```python
node = tree.root_node

# Identity & Type
node.type           # str: Node type (e.g., "function_definition", "identifier")
node.kind_id        # int: Numeric type ID
node.is_named       # bool: True for meaningful nodes, False for punctuation/keywords

# Position Information
node.start_point    # tuple: (row, column) - 0-indexed
node.end_point      # tuple: (row, column)
node.start_byte     # int: Byte offset in source
node.end_byte       # int: Byte offset in source

# Content
node.text           # bytes: The source code this node represents

# Tree Navigation
node.parent         # Node: Parent node (None for root)
node.children       # list[Node]: All child nodes
node.named_children # list[Node]: Only named children (excludes punctuation)
node.child_count    # int: Number of children
node.named_child_count  # int: Number of named children

# Sibling Navigation
node.next_sibling           # Node: Next sibling
node.prev_sibling           # Node: Previous sibling
node.next_named_sibling     # Node: Next named sibling
node.prev_named_sibling     # Node: Previous named sibling

# Error Detection
node.has_error      # bool: True if this node or any descendant has syntax error
node.is_error       # bool: True if this specific node is an error
node.is_missing     # bool: True if parser inserted this to recover from error

# Field Access (language-specific named children)
node.child_by_field_name("name")     # Get child by grammar field name
node.children_by_field_name("body")  # Get all children with field name
```

---

## Tree Traversal Methods

### Method 1: Direct Children Iteration

```python
def print_tree(node, indent=0):
    """Recursively print entire tree structure"""
    prefix = "  " * indent
    text_preview = node.text[:30].decode('utf-8', errors='replace') if node.text else ""
    print(f"{prefix}{node.type}: {text_preview!r}")
    for child in node.children:
        print_tree(child, indent + 1)

print_tree(root)
```

### Method 2: TreeCursor (Most Efficient)

```python
def walk_tree(node):
    """Efficiently walk tree using cursor"""
    cursor = node.walk()
    
    visited = set()
    while True:
        if cursor.node.id not in visited:
            visited.add(cursor.node.id)
            yield cursor.node
        
        # Try to go to first child
        if cursor.goto_first_child():
            continue
        
        # Try to go to next sibling
        if cursor.goto_next_sibling():
            continue
        
        # Go up and try next sibling
        while True:
            if not cursor.goto_parent():
                return
            if cursor.goto_next_sibling():
                break

# Usage
for node in walk_tree(root):
    if node.type == "function_definition":
        name = node.child_by_field_name("name")
        print(f"Found function: {name.text.decode()}")
```

### Method 3: Recursive with Type Filter

```python
def find_nodes_by_type(node, type_name: str) -> list:
    """Find all nodes of a specific type"""
    results = []
    if node.type == type_name:
        results.append(node)
    for child in node.children:
        results.extend(find_nodes_by_type(child, type_name))
    return results

# Find all function definitions
functions = find_nodes_by_type(root, "function_definition")
```

---

## Query System (Pattern Matching)

The query system is the most powerful feature. It uses S-expression patterns to find code structures.

### Basic Query Syntax

```python
language = get_language('python')

# Query pattern syntax:
# (node_type) - matches node type
# (node_type field: (child_type)) - matches with named field
# @capture_name - captures the node for retrieval
# "literal" - matches literal text
# [...] - optional
# * + ? - quantifiers

query = language.query("""
(function_definition
  name: (identifier) @func_name
  parameters: (parameters) @params
  body: (block) @body)
""")

captures = query.captures(root)
# Returns: dict of {capture_name: [list of nodes]}

for name, nodes in captures.items():
    for node in nodes:
        print(f"{name}: {node.text.decode()}")
```

### Common Query Patterns by Language

#### Python

```python
# All function definitions with names
PYTHON_FUNCTIONS = """
(function_definition
  name: (identifier) @name
  parameters: (parameters) @params)
"""

# All class definitions
PYTHON_CLASSES = """
(class_definition
  name: (identifier) @name
  superclasses: (argument_list)? @bases
  body: (block) @body)
"""

# All method definitions (functions inside classes)
PYTHON_METHODS = """
(class_definition
  body: (block
    (function_definition
      name: (identifier) @method_name)))
"""

# All function/method calls
PYTHON_CALLS = """
(call
  function: [
    (identifier) @func_call
    (attribute
      attribute: (identifier) @method_call)
  ])
"""

# All imports
PYTHON_IMPORTS = """
[
  (import_statement
    name: (dotted_name) @import)
  (import_from_statement
    module_name: (dotted_name) @from_module
    name: (dotted_name) @import_name)
]
"""

# All assignments
PYTHON_ASSIGNMENTS = """
(assignment
  left: (identifier) @var_name
  right: (_) @value)
"""

# Decorators
PYTHON_DECORATORS = """
(decorated_definition
  (decorator
    (identifier) @decorator_name)
  definition: (_) @decorated)
"""

# Try/except blocks
PYTHON_TRY_EXCEPT = """
(try_statement
  body: (block) @try_body
  (except_clause
    (identifier)? @exception_type
    body: (block) @except_body)*)
"""

# Docstrings
PYTHON_DOCSTRINGS = """
[
  (module
    . (expression_statement (string) @module_doc))
  (function_definition
    body: (block
      . (expression_statement (string) @func_doc)))
  (class_definition
    body: (block
      . (expression_statement (string) @class_doc)))
]
"""
```

#### JavaScript/TypeScript

```python
# Functions (all types)
JS_FUNCTIONS = """
[
  (function_declaration
    name: (identifier) @name)
  (arrow_function) @arrow
  (function_expression) @func_expr
  (method_definition
    name: (property_identifier) @method_name)
]
"""

# Classes
JS_CLASSES = """
(class_declaration
  name: (identifier) @name
  body: (class_body) @body)
"""

# Imports
JS_IMPORTS = """
[
  (import_statement
    source: (string) @source)
  (import_clause
    (identifier) @default_import)
  (named_imports
    (import_specifier
      name: (identifier) @named_import))
]
"""

# Exports
JS_EXPORTS = """
[
  (export_statement
    declaration: (_) @exported)
  (export_clause
    (export_specifier
      name: (identifier) @export_name))
]
"""

# JSX Elements
JSX_ELEMENTS = """
(jsx_element
  open_tag: (jsx_opening_element
    name: (_) @component_name))
"""
```

#### Go

```python
# Function declarations
GO_FUNCTIONS = """
(function_declaration
  name: (identifier) @name
  parameters: (parameter_list) @params
  result: (_)? @return_type)
"""

# Struct definitions
GO_STRUCTS = """
(type_declaration
  (type_spec
    name: (type_identifier) @name
    type: (struct_type) @struct))
"""

# Interface definitions
GO_INTERFACES = """
(type_declaration
  (type_spec
    name: (type_identifier) @name
    type: (interface_type) @interface))
"""

# Method declarations
GO_METHODS = """
(method_declaration
  receiver: (parameter_list) @receiver
  name: (field_identifier) @name)
"""
```

---

## Complexity Analysis

Tree-sitter enables complexity analysis by counting and analyzing control flow structures.

### Cyclomatic Complexity

```python
def calculate_cyclomatic_complexity(node, language='python'):
    """
    Calculate cyclomatic complexity.
    Formula: 1 + number of decision points
    Decision points: if, elif, for, while, except, and, or, ternary, case
    """
    decision_nodes = {
        'python': [
            'if_statement', 'elif_clause', 'for_statement', 
            'while_statement', 'except_clause', 'with_statement',
            'conditional_expression',  # ternary
            'boolean_operator',  # and/or
            'list_comprehension', 'dictionary_comprehension',
            'set_comprehension', 'generator_expression',
        ],
        'javascript': [
            'if_statement', 'for_statement', 'for_in_statement',
            'while_statement', 'do_statement', 'switch_case',
            'catch_clause', 'ternary_expression', 'binary_expression',
        ],
        'go': [
            'if_statement', 'for_statement', 'expression_case',
            'type_case', 'select_statement', 'communication_case',
        ],
    }
    
    complexity = 1  # Base complexity
    
    def count_decisions(n):
        nonlocal complexity
        if n.type in decision_nodes.get(language, []):
            complexity += 1
            # Special handling for and/or - each adds 1
            if n.type == 'boolean_operator':
                # Count operator occurrences
                pass
        for child in n.children:
            count_decisions(child)
    
    count_decisions(node)
    return complexity


def analyze_function_complexity(code: bytes, language='python'):
    """Analyze complexity of all functions in code"""
    parser = get_parser(language)
    tree = parser.parse(code)
    lang = get_language(language)
    
    func_query = lang.query("""
    (function_definition
      name: (identifier) @name) @func
    """)
    
    results = []
    captures = func_query.captures(tree.root_node)
    
    func_nodes = captures.get('func', [])
    name_nodes = captures.get('name', [])
    
    for func_node, name_node in zip(func_nodes, name_nodes):
        complexity = calculate_cyclomatic_complexity(func_node, language)
        results.append({
            'name': name_node.text.decode(),
            'complexity': complexity,
            'line': func_node.start_point[0] + 1,
            'rating': 'low' if complexity <= 5 else 'medium' if complexity <= 10 else 'high'
        })
    
    return results
```

### Cognitive Complexity

```python
def calculate_cognitive_complexity(node, language='python'):
    """
    Calculate cognitive complexity (Sonar-style).
    Accounts for:
    - Nesting depth (nested structures add more)
    - Structural complexity (loops, conditions)
    - Flow-breaking (break, continue, early returns)
    """
    complexity = 0
    
    structural_nodes = {
        'python': {
            'if_statement': 1, 'elif_clause': 1, 'else_clause': 0,
            'for_statement': 1, 'while_statement': 1,
            'except_clause': 1, 'with_statement': 0,
            'conditional_expression': 1,
            'lambda': 0,
        }
    }
    
    flow_break_nodes = {
        'python': ['break_statement', 'continue_statement', 'return_statement']
    }
    
    def analyze(n, nesting_depth=0):
        nonlocal complexity
        
        node_weight = structural_nodes.get(language, {}).get(n.type, 0)
        if node_weight:
            # Add base complexity + nesting increment
            complexity += node_weight + nesting_depth
        
        # Check for flow breaks (add 1 if breaking from nested context)
        if n.type in flow_break_nodes.get(language, []) and nesting_depth > 0:
            complexity += 1
        
        # Increase nesting for control structures
        new_depth = nesting_depth
        if n.type in ['if_statement', 'for_statement', 'while_statement', 
                      'try_statement', 'with_statement']:
            new_depth = nesting_depth + 1
        
        for child in n.children:
            analyze(child, new_depth)
    
    analyze(node)
    return complexity
```

### Nesting Depth Analysis

```python
def calculate_max_nesting_depth(node, language='python'):
    """Calculate maximum nesting depth of control structures"""
    
    nesting_types = {
        'python': ['if_statement', 'for_statement', 'while_statement',
                   'try_statement', 'with_statement', 'function_definition',
                   'class_definition'],
        'javascript': ['if_statement', 'for_statement', 'while_statement',
                       'try_statement', 'function_declaration', 'arrow_function'],
    }
    
    def max_depth(n, current_depth=0):
        new_depth = current_depth
        if n.type in nesting_types.get(language, []):
            new_depth = current_depth + 1
        
        if not n.children:
            return new_depth
        
        return max(max_depth(child, new_depth) for child in n.children)
    
    return max_depth(node)
```

### Lines of Code Metrics

```python
def calculate_loc_metrics(code: bytes, tree):
    """Calculate various lines of code metrics"""
    lines = code.decode('utf-8', errors='replace').split('\n')
    
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    
    # Find comment lines using tree-sitter
    comment_lines = set()
    
    def find_comments(node):
        if node.type == 'comment':
            for line in range(node.start_point[0], node.end_point[0] + 1):
                comment_lines.add(line)
        for child in node.children:
            find_comments(child)
    
    find_comments(tree.root_node)
    
    code_lines = total_lines - blank_lines - len(comment_lines)
    
    return {
        'total_lines': total_lines,
        'code_lines': code_lines,
        'blank_lines': blank_lines,
        'comment_lines': len(comment_lines),
        'comment_ratio': len(comment_lines) / max(code_lines, 1)
    }
```

---

## Code Structure Extraction

### Extract All Definitions

```python
def extract_definitions(code: bytes, language='python'):
    """Extract all function, class, and variable definitions"""
    parser = get_parser(language)
    tree = parser.parse(code)
    lang = get_language(language)
    
    queries = {
        'python': """
        (function_definition
          name: (identifier) @func_name) @function
        
        (class_definition
          name: (identifier) @class_name) @class
        
        (assignment
          left: (identifier) @var_name) @variable
        """,
        'javascript': """
        (function_declaration
          name: (identifier) @func_name) @function
        
        (class_declaration
          name: (identifier) @class_name) @class
        
        (variable_declarator
          name: (identifier) @var_name) @variable
        """,
    }
    
    query = lang.query(queries.get(language, queries['python']))
    captures = query.captures(tree.root_node)
    
    definitions = {
        'functions': [],
        'classes': [],
        'variables': [],
    }
    
    # Process captures
    for capture_name, nodes in captures.items():
        for node in nodes:
            info = {
                'name': node.text.decode(),
                'line': node.start_point[0] + 1,
                'column': node.start_point[1],
                'end_line': node.end_point[0] + 1,
            }
            
            if capture_name == 'func_name':
                definitions['functions'].append(info)
            elif capture_name == 'class_name':
                definitions['classes'].append(info)
            elif capture_name == 'var_name':
                definitions['variables'].append(info)
    
    return definitions
```

### Extract Call Graph (Within File)

```python
def extract_call_graph(code: bytes, language='python'):
    """Extract which functions call which other functions"""
    parser = get_parser(language)
    tree = parser.parse(code)
    lang = get_language(language)
    
    # First, get all function definitions
    func_query = lang.query("""
    (function_definition
      name: (identifier) @name) @func
    """)
    
    call_query = lang.query("""
    (call
      function: (identifier) @call)
    """)
    
    func_captures = func_query.captures(tree.root_node)
    
    call_graph = {}
    
    # For each function, find calls within its body
    func_nodes = func_captures.get('func', [])
    name_nodes = func_captures.get('name', [])
    
    for func_node, name_node in zip(func_nodes, name_nodes):
        func_name = name_node.text.decode()
        
        # Find all calls within this function
        call_captures = call_query.captures(func_node)
        calls = [n.text.decode() for n in call_captures.get('call', [])]
        
        call_graph[func_name] = {
            'calls': list(set(calls)),
            'line': func_node.start_point[0] + 1,
        }
    
    return call_graph
```

### Extract API Surface

```python
def extract_api_surface(code: bytes, language='python'):
    """Extract public API (exported functions, classes, etc.)"""
    parser = get_parser(language)
    tree = parser.parse(code)
    lang = get_language(language)
    
    if language == 'python':
        # In Python, anything not starting with _ is public
        query = lang.query("""
        (function_definition
          name: (identifier) @name) @func
        (class_definition
          name: (identifier) @name) @class
        """)
        
        captures = query.captures(tree.root_node)
        
        api = {'public': [], 'private': []}
        
        for name, nodes in captures.items():
            if name == 'name':
                continue
            for node in nodes:
                name_node = node.child_by_field_name('name')
                if name_node:
                    symbol_name = name_node.text.decode()
                    info = {
                        'name': symbol_name,
                        'type': 'function' if node.type == 'function_definition' else 'class',
                        'line': node.start_point[0] + 1,
                    }
                    if symbol_name.startswith('_'):
                        api['private'].append(info)
                    else:
                        api['public'].append(info)
        
        return api
    
    elif language in ['javascript', 'typescript']:
        # Look for export statements
        query = lang.query("""
        (export_statement) @export
        """)
        captures = query.captures(tree.root_node)
        return {'exports': [n.text.decode() for n in captures.get('export', [])]}
```

---

## Error Detection and Syntax Validation

### Find Syntax Errors

```python
def find_syntax_errors(code: bytes, language='python'):
    """Find all syntax errors in code"""
    parser = get_parser(language)
    tree = parser.parse(code)
    
    errors = []
    
    def find_errors(node):
        if node.is_error or node.is_missing:
            # Get context around error
            start = max(0, node.start_byte - 20)
            end = min(len(code), node.end_byte + 20)
            context = code[start:end].decode('utf-8', errors='replace')
            
            errors.append({
                'type': 'ERROR' if node.is_error else 'MISSING',
                'line': node.start_point[0] + 1,
                'column': node.start_point[1],
                'text': node.text.decode('utf-8', errors='replace') if node.text else '',
                'context': context,
            })
        
        if node.has_error:
            for child in node.children:
                find_errors(child)
    
    find_errors(tree.root_node)
    return errors


def is_valid_syntax(code: bytes, language='python') -> bool:
    """Quick check if code has valid syntax"""
    parser = get_parser(language)
    tree = parser.parse(code)
    return not tree.root_node.has_error
```

---

## Pattern Detection (Security, Code Smells)

### Security Pattern Detection

```python
def detect_security_patterns(code: bytes, language='python'):
    """Detect potential security issues"""
    parser = get_parser(language)
    tree = parser.parse(code)
    lang = get_language(language)
    
    issues = []
    
    if language == 'python':
        patterns = {
            'eval_usage': """
            (call
              function: (identifier) @func
              (#eq? @func "eval"))
            """,
            'exec_usage': """
            (call
              function: (identifier) @func
              (#eq? @func "exec"))
            """,
            'shell_injection': """
            (call
              function: (attribute
                object: (identifier) @obj
                attribute: (identifier) @method)
              (#eq? @obj "subprocess")
              (#match? @method "call|run|Popen"))
            """,
            'sql_format_string': """
            (call
              function: (attribute
                object: (_)
                attribute: (identifier) @method)
              arguments: (argument_list
                (binary_operator
                  left: (string) @sql
                  (#match? @sql "SELECT|INSERT|UPDATE|DELETE"))))
            """,
            'hardcoded_password': """
            (assignment
              left: (identifier) @var
              right: (string) @value
              (#match? @var "password|passwd|pwd|secret|api_key|token"))
            """,
        }
        
        for issue_type, pattern in patterns.items():
            try:
                query = lang.query(pattern)
                captures = query.captures(tree.root_node)
                if captures:
                    for name, nodes in captures.items():
                        for node in nodes:
                            issues.append({
                                'type': issue_type,
                                'line': node.start_point[0] + 1,
                                'text': node.text.decode(),
                            })
            except Exception:
                pass  # Skip invalid patterns
    
    return issues
```

### Code Smell Detection

```python
def detect_code_smells(code: bytes, language='python'):
    """Detect common code smells"""
    parser = get_parser(language)
    tree = parser.parse(code)
    
    smells = []
    
    # Long functions (by line count)
    def check_long_functions(node, threshold=50):
        if node.type == 'function_definition':
            line_count = node.end_point[0] - node.start_point[0]
            if line_count > threshold:
                name = node.child_by_field_name('name')
                smells.append({
                    'type': 'long_function',
                    'name': name.text.decode() if name else 'anonymous',
                    'lines': line_count,
                    'line': node.start_point[0] + 1,
                })
        for child in node.children:
            check_long_functions(child, threshold)
    
    # Too many parameters
    def check_parameter_count(node, threshold=5):
        if node.type == 'function_definition':
            params = node.child_by_field_name('parameters')
            if params:
                param_count = len([c for c in params.children if c.is_named])
                if param_count > threshold:
                    name = node.child_by_field_name('name')
                    smells.append({
                        'type': 'too_many_parameters',
                        'name': name.text.decode() if name else 'anonymous',
                        'count': param_count,
                        'line': node.start_point[0] + 1,
                    })
        for child in node.children:
            check_parameter_count(child, threshold)
    
    # Deeply nested code
    def check_nesting(node, current_depth=0, threshold=4):
        nesting_types = ['if_statement', 'for_statement', 'while_statement', 
                         'try_statement', 'with_statement']
        
        new_depth = current_depth + 1 if node.type in nesting_types else current_depth
        
        if new_depth > threshold:
            smells.append({
                'type': 'deep_nesting',
                'depth': new_depth,
                'line': node.start_point[0] + 1,
                'node_type': node.type,
            })
        
        for child in node.children:
            check_nesting(child, new_depth, threshold)
    
    check_long_functions(tree.root_node)
    check_parameter_count(tree.root_node)
    check_nesting(tree.root_node)
    
    return smells
```

---

## Incremental Parsing

For real-time editing or large files:

```python
def incremental_update(tree, code: bytes, edit_start: int, old_end: int, new_end: int):
    """
    Update tree after an edit without full re-parse.
    
    Args:
        tree: Existing parsed tree
        code: New code after edit
        edit_start: Byte offset where edit started
        old_end: Byte offset where old text ended
        new_end: Byte offset where new text ends
    """
    # Calculate point positions
    old_code_len = old_end - edit_start
    new_code_len = new_end - edit_start
    
    # Tell tree-sitter about the edit
    tree.edit(
        start_byte=edit_start,
        old_end_byte=old_end,
        new_end_byte=new_end,
        start_point=(0, edit_start),  # Simplified - should calculate actual point
        old_end_point=(0, old_end),
        new_end_point=(0, new_end),
    )
    
    # Re-parse with old tree (much faster)
    parser = get_parser('python')
    new_tree = parser.parse(code, tree)
    
    return new_tree
```

---

## Multi-Language Project Analysis

```python
from pathlib import Path

LANGUAGE_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.jsx': 'javascript',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java',
    '.rb': 'ruby',
    '.php': 'php',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
}

def analyze_project(root_path: str):
    """Analyze all supported files in a project"""
    root = Path(root_path)
    results = {
        'files': [],
        'total_functions': 0,
        'total_classes': 0,
        'total_lines': 0,
        'by_language': {},
    }
    
    for ext, language in LANGUAGE_EXTENSIONS.items():
        for file_path in root.rglob(f'*{ext}'):
            # Skip common non-source directories
            if any(part.startswith('.') or part in ['node_modules', 'venv', '__pycache__'] 
                   for part in file_path.parts):
                continue
            
            try:
                with open(file_path, 'rb') as f:
                    code = f.read()
                
                parser = get_parser(language)
                tree = parser.parse(code)
                
                defs = extract_definitions(code, language)
                metrics = calculate_loc_metrics(code, tree)
                
                file_result = {
                    'path': str(file_path),
                    'language': language,
                    'functions': len(defs['functions']),
                    'classes': len(defs['classes']),
                    **metrics,
                }
                
                results['files'].append(file_result)
                results['total_functions'] += len(defs['functions'])
                results['total_classes'] += len(defs['classes'])
                results['total_lines'] += metrics['total_lines']
                
                # Aggregate by language
                if language not in results['by_language']:
                    results['by_language'][language] = {
                        'files': 0, 'functions': 0, 'classes': 0, 'lines': 0
                    }
                results['by_language'][language]['files'] += 1
                results['by_language'][language]['functions'] += len(defs['functions'])
                results['by_language'][language]['classes'] += len(defs['classes'])
                results['by_language'][language]['lines'] += metrics['total_lines']
                
            except Exception as e:
                results['files'].append({
                    'path': str(file_path),
                    'error': str(e),
                })
    
    return results
```

---

## Summary: What py-tree-sitter CAN Do

| Capability | Description |
|------------|-------------|
| **Parse any supported language** | 30+ languages with unified API |
| **Extract structure** | Functions, classes, methods, variables, imports |
| **Measure complexity** | Cyclomatic, cognitive, nesting depth |
| **Calculate metrics** | LOC, comment ratio, function length |
| **Detect patterns** | Security issues, code smells, anti-patterns |
| **Find syntax errors** | Locate and describe parse errors |
| **Query code** | Powerful pattern matching with capture groups |
| **Build call graphs** | Within-file function call relationships |
| **Navigate AST** | Efficient tree traversal with cursors |
| **Incremental parsing** | Fast re-parse after edits |

## What py-tree-sitter CANNOT Do (Without Extra Work)

| Limitation | Why |
|------------|-----|
| **Cross-file analysis** | Each file parsed independently |
| **Dead code detection** | No reference tracking between files |
| **Type inference** | Purely syntactic, no semantic analysis |
| **Resolve imports** | Doesn't follow import statements |
| **Dynamic code analysis** | Can't understand `eval()` or `getattr()` |

---

## Quick Reference: Node Types by Language

### Python
- `module`, `function_definition`, `class_definition`
- `if_statement`, `for_statement`, `while_statement`, `try_statement`
- `import_statement`, `import_from_statement`
- `assignment`, `expression_statement`, `return_statement`
- `call`, `attribute`, `identifier`, `string`, `integer`

### JavaScript/TypeScript
- `program`, `function_declaration`, `class_declaration`
- `if_statement`, `for_statement`, `while_statement`
- `import_statement`, `export_statement`
- `variable_declaration`, `lexical_declaration`
- `call_expression`, `member_expression`, `identifier`

### Go
- `source_file`, `function_declaration`, `method_declaration`
- `type_declaration`, `struct_type`, `interface_type`
- `if_statement`, `for_statement`, `select_statement`
- `import_declaration`, `package_clause`
- `call_expression`, `selector_expression`, `identifier`

---

## Recommended Experiments

1. **Parse a file and print the tree** - understand the structure
2. **Write queries for your common patterns** - functions, classes, imports
3. **Calculate complexity for a real file** - compare to your intuition
4. **Detect code smells in your codebase** - long functions, deep nesting
5. **Build a simple linter rule** - e.g., "no print statements in production code"
6. **Extract documentation** - find all docstrings and comments
7. **Compare files** - extract structure from two versions
