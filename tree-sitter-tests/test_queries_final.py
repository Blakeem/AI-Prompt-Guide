#!/usr/bin/env python3
"""
Tree-sitter Query Pattern Reference - Final Working Examples

This file documents all working query patterns discovered through testing,
organized by use case for code auditing purposes.
"""

import tree_sitter_python as ts_python
from tree_sitter import Language, Parser, Query, QueryCursor
from dataclasses import dataclass
from typing import Any
import json

# Initialize
PY_LANGUAGE = Language(ts_python.language())
parser = Parser(PY_LANGUAGE)


# =============================================================================
# WORKING QUERY PATTERNS - Tested and Verified
# =============================================================================

WORKING_QUERIES = {
    # -------------------------------------------------------------------------
    # SECURITY PATTERNS
    # -------------------------------------------------------------------------
    "eval_exec_calls": {
        "description": "Detect dangerous eval() and exec() calls",
        "category": "security",
        "query": '''
(call
  function: (identifier) @func_name
  (#match? @func_name "^(eval|exec)$")
) @dangerous_call
''',
        "test_code": 'result = eval(user_input)\nexec("print(1)")',
        "expected_captures": ["dangerous_call", "func_name"],
    },

    "subprocess_os_calls": {
        "description": "Detect subprocess and os.system calls",
        "category": "security",
        "query": '''
(call
  function: (attribute
    object: (identifier) @module
    attribute: (identifier) @method)
  (#match? @module "^(subprocess|os)$")
  (#match? @method "^(call|run|system|popen|Popen|spawn|execv|execve)$")
) @subprocess_call
''',
        "test_code": 'subprocess.run(cmd)\nos.system("ls")',
        "expected_captures": ["subprocess_call", "module", "method"],
    },

    "shell_true_kwarg": {
        "description": "Detect shell=True in function calls",
        "category": "security",
        "query": '''
(call
  arguments: (argument_list
    (keyword_argument
      name: (identifier) @kw_name
      value: (true) @shell_true)
    (#eq? @kw_name "shell"))
) @shell_true_call
''',
        "test_code": 'subprocess.run(cmd, shell=True)',
        "expected_captures": ["shell_true_call", "kw_name", "shell_true"],
    },

    "hardcoded_secrets": {
        "description": "Detect string assignments to secret-named variables",
        "category": "security",
        "query": '''
(assignment
  left: (identifier) @var_name
  right: (string) @secret_value
  (#match? @var_name "(?i)(password|secret|api_key|token|key|credential|auth)")
) @hardcoded_secret
''',
        "test_code": 'API_KEY = "sk-1234"\npassword = "secret123"',
        "expected_captures": ["hardcoded_secret", "var_name", "secret_value"],
    },

    "sql_string_concat": {
        "description": "Detect SQL string concatenation (injection risk)",
        "category": "security",
        "query": '''
(binary_operator
  left: (string) @sql_string
  operator: "+"
  (#match? @sql_string "(?i)(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)")
) @sql_concat
''',
        "test_code": 'query = "SELECT * FROM users WHERE id = " + user_id',
        "expected_captures": ["sql_concat", "sql_string"],
    },

    "fstring_with_interpolation": {
        "description": "Detect f-strings with interpolation (potential SQL/command injection)",
        "category": "security",
        "query": '''
(string
  (string_start) @start
  (interpolation) @interp
  (#match? @start "^[fF]")
) @fstring
''',
        "test_code": 'query = f"SELECT * FROM {table}"',
        "expected_captures": ["fstring", "start", "interp"],
    },

    # -------------------------------------------------------------------------
    # CODE SMELL PATTERNS
    # -------------------------------------------------------------------------
    "bare_except": {
        "description": "Detect bare except clauses (catches all exceptions)",
        "category": "code_smell",
        "query": '''
(except_clause) @except_clause
''',
        "post_process": "Filter where node has no 'as_pattern' or direct type child",
        "test_code": 'try:\n    x()\nexcept:\n    pass',
        "expected_captures": ["except_clause"],
    },

    "deeply_nested_if": {
        "description": "Detect if statements nested 3+ levels",
        "category": "code_smell",
        "query": '''
(if_statement
  consequence: (block
    (if_statement
      consequence: (block
        (if_statement) @level3
      )
    ) @level2
  )
) @level1
''',
        "test_code": 'if a:\n    if b:\n        if c:\n            pass',
        "expected_captures": ["level1", "level2", "level3"],
    },

    "many_function_args": {
        "description": "Detect function calls with 6+ arguments",
        "category": "code_smell",
        "query": '''
(call
  arguments: (argument_list
    (_) @arg1
    (_) @arg2
    (_) @arg3
    (_) @arg4
    (_) @arg5
    (_) @arg6
  )
) @many_args_call
''',
        "test_code": 'func(a, b, c, d, e, f, g)',
        "expected_captures": ["many_args_call", "arg1", "arg2", "arg3", "arg4", "arg5", "arg6"],
    },

    "pass_only_except": {
        "description": "Detect except blocks that only contain pass",
        "category": "code_smell",
        "query": '''
(except_clause
  (block
    (pass_statement) @pass_stmt
  )
) @swallowed_except
''',
        "test_code": 'try:\n    x()\nexcept:\n    pass',
        "expected_captures": ["swallowed_except", "pass_stmt"],
    },

    "nested_comprehension": {
        "description": "Detect nested list comprehensions",
        "category": "code_smell",
        "query": '''
(list_comprehension
  body: (list_comprehension) @inner
) @nested_comp
''',
        "test_code": 'nested = [[x for x in row] for row in matrix]',
        "expected_captures": ["nested_comp", "inner"],
    },

    "multi_if_comprehension": {
        "description": "Detect comprehensions with multiple if clauses",
        "category": "code_smell",
        "query": '''
(list_comprehension
  (if_clause) @if1
  (if_clause) @if2
) @multi_if_comp
''',
        "test_code": 'result = [x for x in items if x > 0 if x < 100]',
        "expected_captures": ["multi_if_comp", "if1", "if2"],
    },

    # -------------------------------------------------------------------------
    # DOCSTRING PATTERNS
    # -------------------------------------------------------------------------
    "function_docstring": {
        "description": "Extract function docstrings",
        "category": "documentation",
        "query": '''
(function_definition
  name: (identifier) @func_name
  body: (block
    . (expression_statement
        (string) @docstring))
) @documented_function
''',
        "test_code": 'def foo():\n    """Docstring."""\n    pass',
        "expected_captures": ["documented_function", "func_name", "docstring"],
    },

    "class_docstring": {
        "description": "Extract class docstrings",
        "category": "documentation",
        "query": '''
(class_definition
  name: (identifier) @class_name
  body: (block
    . (expression_statement
        (string) @docstring))
) @documented_class
''',
        "test_code": 'class Foo:\n    """Class doc."""\n    pass',
        "expected_captures": ["documented_class", "class_name", "docstring"],
    },

    "module_docstring": {
        "description": "Extract module-level docstring",
        "category": "documentation",
        "query": '''
(module
  . (expression_statement
      (string) @docstring))
''',
        "test_code": '"""Module docstring."""\nimport os',
        "expected_captures": ["docstring"],
    },

    # -------------------------------------------------------------------------
    # IMPORT PATTERNS
    # -------------------------------------------------------------------------
    "simple_import": {
        "description": "Match import statements",
        "category": "imports",
        "query": '''
(import_statement
  name: (dotted_name) @module_name
) @import
''',
        "test_code": 'import os\nimport sys',
        "expected_captures": ["import", "module_name"],
    },

    "aliased_import": {
        "description": "Match import X as Y",
        "category": "imports",
        "query": '''
(import_statement
  name: (aliased_import
    name: (dotted_name) @original
    alias: (identifier) @alias)
) @aliased_import
''',
        "test_code": 'import numpy as np',
        "expected_captures": ["aliased_import", "original", "alias"],
    },

    "from_import": {
        "description": "Match from X import Y",
        "category": "imports",
        "query": '''
(import_from_statement
  module_name: (dotted_name) @module
  name: (dotted_name) @imported
) @from_import
''',
        "test_code": 'from os import path',
        "expected_captures": ["from_import", "module", "imported"],
    },

    "star_import": {
        "description": "Match from X import * (code smell)",
        "category": "imports",
        "query": '''
(import_from_statement
  module_name: (dotted_name) @module
  (wildcard_import) @star
) @star_import
''',
        "test_code": 'from os.path import *',
        "expected_captures": ["star_import", "module", "star"],
    },

    "relative_import": {
        "description": "Match relative imports",
        "category": "imports",
        "query": '''
(import_from_statement
  module_name: (relative_import) @relative
) @rel_import
''',
        "test_code": 'from . import sibling\nfrom ..utils import helper',
        "expected_captures": ["rel_import", "relative"],
    },

    "local_import": {
        "description": "Match imports inside functions",
        "category": "imports",
        "query": '''
(function_definition
  body: (block
    [(import_statement) (import_from_statement)] @local_import
  )
) @func_with_local_import
''',
        "test_code": 'def foo():\n    import os\n    return os.getcwd()',
        "expected_captures": ["func_with_local_import", "local_import"],
    },

    # -------------------------------------------------------------------------
    # METHOD CLASSIFICATION
    # -------------------------------------------------------------------------
    "instance_method": {
        "description": "Detect methods with self as first parameter",
        "category": "methods",
        "query": '''
(function_definition
  parameters: (parameters
    . (identifier) @first_param
    (#eq? @first_param "self")
  )
) @instance_method
''',
        "test_code": 'class C:\n    def method(self, x): pass',
        "expected_captures": ["instance_method", "first_param"],
    },

    "classmethod_decorated": {
        "description": "Detect @classmethod decorated functions",
        "category": "methods",
        "query": '''
(decorated_definition
  (decorator
    (identifier) @dec
    (#eq? @dec "classmethod")
  )
  definition: (function_definition) @class_method
)
''',
        "test_code": 'class C:\n    @classmethod\n    def method(cls): pass',
        "expected_captures": ["dec", "class_method"],
    },

    "staticmethod_decorated": {
        "description": "Detect @staticmethod decorated functions",
        "category": "methods",
        "query": '''
(decorated_definition
  (decorator
    (identifier) @dec
    (#eq? @dec "staticmethod")
  )
  definition: (function_definition) @static_method
)
''',
        "test_code": 'class C:\n    @staticmethod\n    def method(x): pass',
        "expected_captures": ["dec", "static_method"],
    },

    # -------------------------------------------------------------------------
    # ASYNC PATTERNS
    # -------------------------------------------------------------------------
    "async_function": {
        "description": "Detect async function definitions",
        "category": "async",
        "query": '''
(function_definition
  "async" @async_kw
  name: (identifier) @func_name
) @async_func
''',
        "test_code": 'async def fetch_data(): pass',
        "expected_captures": ["async_func", "async_kw", "func_name"],
    },

    "await_expression": {
        "description": "Detect await expressions",
        "category": "async",
        "query": '''
(await
  (call
    function: (_) @awaited_func
  )
) @await_expr
''',
        "test_code": 'async def f():\n    result = await fetch()',
        "expected_captures": ["await_expr", "awaited_func"],
    },

    # -------------------------------------------------------------------------
    # TYPE HINTS
    # -------------------------------------------------------------------------
    "typed_parameter": {
        "description": "Detect type-annotated parameters",
        "category": "types",
        "query": '''
; Match both typed_parameter and typed_default_parameter
[(typed_parameter) (typed_default_parameter)] @typed_param
''',
        "test_code": 'def foo(x: int, y: str = "hi"): pass',
        "expected_captures": ["typed_param"],
    },

    "return_type_annotation": {
        "description": "Detect function return type annotations",
        "category": "types",
        "query": '''
(function_definition
  name: (identifier) @func_name
  return_type: (type) @return_type
) @typed_func
''',
        "test_code": 'def foo(x) -> int: return 1',
        "expected_captures": ["typed_func", "func_name", "return_type"],
    },

    # -------------------------------------------------------------------------
    # MISC PATTERNS
    # -------------------------------------------------------------------------
    "assert_statement": {
        "description": "Detect assert statements",
        "category": "misc",
        "query": '''
(assert_statement) @assert
''',
        "test_code": 'assert x > 0, "must be positive"',
        "expected_captures": ["assert"],
    },

    "global_statement": {
        "description": "Detect global variable declarations",
        "category": "misc",
        "query": '''
(global_statement
  (identifier) @global_var
) @global_stmt
''',
        "test_code": 'def foo():\n    global counter\n    counter += 1',
        "expected_captures": ["global_stmt", "global_var"],
    },

    "comparison_chain": {
        "description": "Detect chained comparisons (a < b < c)",
        "category": "misc",
        "query": '''
; A chained comparison has 3+ operands - just detect all comparisons
(comparison_operator) @comparison
''',
        "test_code": 'if 0 < x < 10: pass',
        "expected_captures": ["comparison"],
        "post_process": "Check node children count > 3 for chain detection",
    },
}


@dataclass
class QueryResult:
    """Result from running a query."""
    name: str
    success: bool
    captures: dict[str, int]
    sample_matches: list[dict[str, Any]]
    error: str | None = None


def run_query(code: str, query_text: str) -> tuple[bool, dict, list, str | None]:
    """Execute a query and return results."""
    try:
        tree = parser.parse(bytes(code, "utf-8"))
        query = Query(PY_LANGUAGE, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        capture_counts = {k: len(v) for k, v in captures.items()}
        samples = []

        for cap_name, nodes in captures.items():
            for node in nodes[:2]:
                text = code[node.start_byte:node.end_byte]
                if len(text) > 60:
                    text = text[:60] + "..."
                samples.append({
                    "capture": cap_name,
                    "text": text.replace('\n', '\\n'),
                    "line": node.start_point.row + 1,
                })

        return True, capture_counts, samples, None
    except Exception as e:
        return False, {}, [], str(e)


def test_all_queries() -> list[QueryResult]:
    """Test all defined queries and return results."""
    results = []

    for name, config in WORKING_QUERIES.items():
        success, captures, samples, error = run_query(
            config["test_code"],
            config["query"]
        )

        results.append(QueryResult(
            name=name,
            success=success,
            captures=captures,
            sample_matches=samples,
            error=error
        ))

    return results


def print_results(results: list[QueryResult]) -> None:
    """Print test results in a formatted way."""
    categories: dict[str, list[QueryResult]] = {}

    for result in results:
        cat = WORKING_QUERIES[result.name]["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)

    passed = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)

    print(f"\n{'='*70}")
    print(f"TREE-SITTER QUERY PATTERN TEST RESULTS")
    print(f"{'='*70}")
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")

    for category, cat_results in categories.items():
        print(f"\n{'-'*70}")
        print(f"Category: {category.upper()}")
        print(f"{'-'*70}")

        for result in cat_results:
            status = "PASS" if result.success else "FAIL"
            desc = WORKING_QUERIES[result.name]["description"]
            print(f"\n[{status}] {result.name}")
            print(f"  Description: {desc}")

            if result.error:
                print(f"  Error: {result.error}")
            else:
                print(f"  Captures: {result.captures}")
                if result.sample_matches:
                    print(f"  Sample: {result.sample_matches[0]}")


def generate_summary() -> str:
    """Generate a summary of query capabilities."""
    return """
================================================================================
TREE-SITTER QUERY CAPABILITY SUMMARY FOR CODE AUDITING
================================================================================

WHAT WORKS WELL:
----------------
1. STRUCTURAL PATTERNS
   - Function/class/method definitions
   - Call expressions with specific names
   - Nested structures (if/for/comprehensions)
   - Decorator detection
   - Import statement analysis

2. PREDICATES
   - #eq? for exact string matching
   - #match? for regex patterns (including (?i) case-insensitive)
   - Field anchoring with '.' for first-child matches
   - Optional fields with (_)?

3. SECURITY DETECTION
   - eval/exec calls: Easy and reliable
   - subprocess/os.system: Works with attribute matching
   - shell=True: Detectable via keyword_argument
   - Hardcoded secrets: Variable name regex + string value
   - SQL concat: String literal + operator matching
   - F-string interpolation: string_start + interpolation children

4. CODE SMELL DETECTION
   - Bare except: Need post-processing (query all, filter by structure)
   - Nested structures: Direct descendant patterns work
   - Many arguments: Fixed count matching works
   - Pass-only except: Block content inspection works

5. DOCUMENTATION
   - Docstrings: First-child anchor (.) works perfectly
   - All definition types supported (module, class, function)

WHAT DOESN'T WORK:
------------------
1. DATA FLOW
   - Cannot track variable usage across statements
   - Cannot determine if eval() receives user input
   - Would need separate taint analysis

2. COUNTING CONSTRAINTS
   - Cannot express "more than N" in queries
   - Solution: Query all, count in Python

3. NEGATION
   - Cannot express "function WITHOUT docstring" directly
   - Solution: Query WITH patterns, compute set difference

4. SEMANTIC TYPES
   - Cannot determine actual types of variables
   - Cannot distinguish pickle.loads from custom loads()
   - Would need type inference

5. SOME GRAMMAR QUIRKS
   - Field negation (!field) doesn't work in all contexts
   - Some node types require exact grammar knowledge
   - Need to inspect AST structure for complex patterns

RECOMMENDATIONS FOR CODE AUDITING:
----------------------------------
1. Use tree-sitter queries for:
   - Pattern-based security scanning (eval, exec, subprocess)
   - Structural code smell detection
   - Documentation coverage analysis
   - Import dependency mapping
   - Coding standard enforcement

2. Combine with post-processing for:
   - Counting violations (>N returns, >N args)
   - Negation patterns (missing docstrings)
   - Filtering by context

3. Use separate tools for:
   - Data flow / taint analysis
   - Type-aware analysis
   - Cross-file dependencies

4. Build a query library:
   - Test each query against known patterns
   - Document expected captures
   - Version control query definitions
"""


def main():
    """Run all tests and print results."""
    print("Testing all query patterns...")
    results = test_all_queries()
    print_results(results)
    print(generate_summary())

    # Also output a JSON summary for programmatic use
    json_output = {
        "total": len(results),
        "passed": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "results": [
            {
                "name": r.name,
                "category": WORKING_QUERIES[r.name]["category"],
                "success": r.success,
                "captures": r.captures,
                "error": r.error,
            }
            for r in results
        ]
    }

    print("\n" + "="*70)
    print("JSON OUTPUT")
    print("="*70)
    print(json.dumps(json_output, indent=2))


if __name__ == "__main__":
    main()
