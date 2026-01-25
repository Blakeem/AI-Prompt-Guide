#!/usr/bin/env python3
"""
Tree-sitter Query Pattern Capability Test

Tests tree-sitter's query capabilities for:
- Security pattern detection
- Code smell detection
- Docstring extraction
- Import analysis

Uses tree-sitter 0.25.2 API with tree-sitter-python.
"""

import tree_sitter_python as ts_python
from tree_sitter import Language, Parser, Query, QueryCursor
from typing import Any
import textwrap

# Initialize language and parser
PY_LANGUAGE = Language(ts_python.language())
parser = Parser(PY_LANGUAGE)


# =============================================================================
# Test Code Samples
# =============================================================================

SECURITY_TEST_CODE = '''
import os
import subprocess
from pickle import loads

# Dangerous eval/exec usage
user_input = input("Enter code: ")
result = eval(user_input)  # SECURITY: eval with user input
exec(compile(user_input, "<string>", "exec"))  # SECURITY: exec usage

# Subprocess calls - potential command injection
subprocess.call(["ls", "-la"])
subprocess.run(user_input, shell=True)  # SECURITY: shell=True with user input
os.system("rm -rf /")  # SECURITY: os.system call

# Hardcoded secrets
API_KEY = "sk-1234567890abcdef"  # SECURITY: hardcoded API key
password = "super_secret_password123"  # SECURITY: hardcoded password
SECRET_TOKEN = "ghp_abcdefghijklmnop"  # SECURITY: GitHub token pattern

# SQL injection patterns
query = "SELECT * FROM users WHERE id = " + user_id  # SECURITY: string concat SQL
cursor.execute(f"DELETE FROM users WHERE name = '{name}'")  # SECURITY: f-string SQL

# Pickle deserialization
data = loads(untrusted_data)  # SECURITY: pickle loads

# Insecure random
import random
token = random.random()  # SECURITY: not cryptographically secure
'''

CODE_SMELL_TEST_CODE = '''
def complex_function(x, y, z):
    """A function with multiple code smells."""
    # Nested ternary - hard to read
    result = "a" if x > 0 else ("b" if y > 0 else ("c" if z > 0 else "d"))

    # Multiple returns scattered throughout
    if x < 0:
        return None

    if y < 0:
        return -1

    # Bare except - catches everything including KeyboardInterrupt
    try:
        risky_operation()
    except:
        pass  # Swallowing all exceptions

    # Another bare except
    try:
        another_risky()
    except:
        return False

    # Magic numbers
    if x > 42 and y < 3.14159:
        return x * 1337

    # Too many arguments in a function call (not this function, but calling one)
    some_func(a, b, c, d, e, f, g, h, i, j)

    return result


def another_function():
    # Long function with many returns
    if condition1:
        return 1
    if condition2:
        return 2
    if condition3:
        return 3
    if condition4:
        return 4
    return 5


# Deeply nested code
def nested_nightmare():
    if a:
        if b:
            if c:
                if d:
                    if e:
                        do_something()
'''

DOCSTRING_TEST_CODE = '''
"""Module-level docstring for the test module.

This module demonstrates docstring extraction capabilities.
"""

class MyClass:
    """Class docstring for MyClass.

    This class does interesting things.

    Attributes:
        name: The name of the instance
        value: Some numeric value
    """

    def __init__(self, name: str, value: int):
        """Initialize MyClass.

        Args:
            name: The name to use
            value: The initial value
        """
        self.name = name
        self.value = value

    def process(self, data: list) -> dict:
        """Process the input data.

        This method takes a list and returns a dictionary.

        Args:
            data: Input list to process

        Returns:
            A dictionary with processed results

        Raises:
            ValueError: If data is empty
        """
        pass

    def no_docstring_method(self):
        pass


def standalone_function(arg1, arg2):
    """A standalone function with a docstring."""
    return arg1 + arg2


def no_docstring():
    return 42


async def async_function():
    """Async function docstring."""
    await something()
'''

IMPORT_TEST_CODE = '''
# Standard imports
import os
import sys
import json
from pathlib import Path

# From imports with multiple names
from collections import defaultdict, OrderedDict, Counter
from typing import List, Dict, Optional, Union, Any

# Aliased imports
import numpy as np
import pandas as pd
from datetime import datetime as dt

# Relative imports
from . import sibling_module
from .. import parent_module
from ..utils import helper_function

# Star imports (code smell)
from os.path import *

# Conditional imports
try:
    import ujson as json
except ImportError:
    import json

# Nested/local imports (inside function - another pattern)
def func_with_local_import():
    import tempfile
    from io import StringIO
    return tempfile.mktemp()
'''


# =============================================================================
# Query Definitions
# =============================================================================

SECURITY_QUERIES = {
    "eval_exec_usage": '''
    ; Match calls to eval() or exec()
    (call
      function: (identifier) @func_name
      (#match? @func_name "^(eval|exec)$")
    ) @dangerous_call
    ''',

    "subprocess_calls": '''
    ; Match subprocess module calls
    (call
      function: (attribute
        object: (identifier) @module
        attribute: (identifier) @method)
      (#match? @module "^(subprocess|os)$")
      (#match? @method "^(call|run|system|popen|Popen|spawn)$")
    ) @subprocess_call
    ''',

    "shell_true_pattern": '''
    ; Match shell=True in function calls
    (call
      arguments: (argument_list
        (keyword_argument
          name: (identifier) @kw_name
          value: (true) @shell_true)
        (#eq? @kw_name "shell"))
    ) @shell_true_call
    ''',

    "hardcoded_secrets_assignment": '''
    ; Match assignments with secret-like names
    (assignment
      left: (identifier) @var_name
      right: (string) @secret_value
      (#match? @var_name "(?i)(password|secret|api_key|token|key|credential)")
    ) @hardcoded_secret
    ''',

    "sql_string_concat": '''
    ; Match string concatenation that might be SQL
    (binary_operator
      left: (string) @sql_string
      operator: "+"
      (#match? @sql_string "(?i)(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)")
    ) @sql_concat
    ''',

    "pickle_loads": '''
    ; Match pickle.loads or loads from pickle
    (call
      function: [
        (attribute
          object: (identifier) @module
          attribute: (identifier) @method
          (#eq? @module "pickle")
          (#eq? @method "loads"))
        (identifier) @func
        (#eq? @func "loads")
      ]
    ) @pickle_loads
    ''',
}

CODE_SMELL_QUERIES = {
    "bare_except": '''
    ; Match bare except clauses (no exception type)
    (except_clause
      !type
    ) @bare_except
    ''',

    "nested_ternary": '''
    ; Match conditional expressions nested inside other conditional expressions
    (conditional_expression
      body: (conditional_expression) @inner_ternary
    ) @nested_ternary
    ''',

    "nested_ternary_alt": '''
    ; Also check alternative position
    (conditional_expression
      alternative: (conditional_expression) @inner_ternary
    ) @nested_ternary_alt
    ''',

    "return_statements": '''
    ; Match all return statements in functions
    (function_definition
      body: (block
        (return_statement) @return
      )
    ) @function_with_return
    ''',

    "deeply_nested_if": '''
    ; Match if statements nested 3+ levels deep
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

    "many_function_args": '''
    ; Match function calls with many arguments (6+)
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

    "pass_in_except": '''
    ; Match except blocks that just pass
    (except_clause
      body: (block
        (pass_statement) @pass
      )
    ) @swallowed_exception
    ''',
}

DOCSTRING_QUERIES = {
    "module_docstring": '''
    ; Match module-level docstring (first statement is expression with string)
    (module
      (expression_statement
        (string) @docstring
      ) @first_stmt
      (#is-first-child? @first_stmt)
    )
    ''',

    "module_docstring_simple": '''
    ; Simpler: just get first string expression in module
    (module
      (expression_statement
        (string) @module_docstring) @doc_stmt)
    ''',

    "function_docstring": '''
    ; Match function docstrings
    (function_definition
      name: (identifier) @func_name
      body: (block
        (expression_statement
          (string) @docstring) @first_stmt)
    ) @documented_function
    ''',

    "class_docstring": '''
    ; Match class docstrings
    (class_definition
      name: (identifier) @class_name
      body: (block
        (expression_statement
          (string) @docstring) @first_stmt)
    ) @documented_class
    ''',

    "method_docstring": '''
    ; Match method docstrings (functions inside classes)
    (class_definition
      body: (block
        (function_definition
          name: (identifier) @method_name
          body: (block
            (expression_statement
              (string) @docstring))
        ) @documented_method
      )
    )
    ''',

    "undocumented_function": '''
    ; Match functions without docstrings - harder to express directly
    ; This finds functions where first statement is NOT a string expression
    (function_definition
      name: (identifier) @func_name
      body: (block
        . (_) @first_stmt)
      (#not-kind-eq? @first_stmt "expression_statement")
    ) @undocumented_function
    ''',
}

IMPORT_QUERIES = {
    "simple_import": '''
    ; Match import statements
    (import_statement
      name: (dotted_name) @module_name
    ) @import
    ''',

    "aliased_import": '''
    ; Match aliased imports (import X as Y)
    (import_statement
      name: (aliased_import
        name: (dotted_name) @original_name
        alias: (identifier) @alias_name)
    ) @aliased_import
    ''',

    "from_import": '''
    ; Match from X import Y
    (import_from_statement
      module_name: (dotted_name) @module
      name: (dotted_name) @imported_name
    ) @from_import
    ''',

    "from_import_aliased": '''
    ; Match from X import Y as Z
    (import_from_statement
      module_name: (dotted_name) @module
      name: (aliased_import
        name: (dotted_name) @imported_name
        alias: (identifier) @alias)
    ) @from_import_aliased
    ''',

    "star_import": '''
    ; Match from X import * (code smell)
    (import_from_statement
      module_name: (dotted_name) @module
      (wildcard_import) @star
    ) @star_import
    ''',

    "relative_import": '''
    ; Match relative imports (from . or from ..)
    (import_from_statement
      module_name: (relative_import) @relative_path
    ) @relative_import
    ''',

    "local_import": '''
    ; Match imports inside functions
    (function_definition
      body: (block
        [(import_statement) (import_from_statement)] @local_import
      )
    ) @function_with_local_import
    ''',
}


# =============================================================================
# Query Execution and Analysis
# =============================================================================

def run_query(code: str, query_text: str, query_name: str) -> dict[str, Any]:
    """Execute a query and return results with metadata."""
    result = {
        "query_name": query_name,
        "success": False,
        "error": None,
        "captures": {},
        "match_count": 0,
        "captured_text": [],
    }

    try:
        tree = parser.parse(bytes(code, "utf-8"))
        query = Query(PY_LANGUAGE, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        result["success"] = True
        result["captures"] = {k: len(v) for k, v in captures.items()}
        result["match_count"] = sum(len(v) for v in captures.values())

        # Extract actual text for key captures
        for capture_name, nodes in captures.items():
            for node in nodes[:5]:  # Limit to first 5 per capture
                text = code[node.start_byte:node.end_byte]
                # Truncate long strings
                if len(text) > 100:
                    text = text[:100] + "..."
                result["captured_text"].append({
                    "capture": capture_name,
                    "text": text,
                    "line": node.start_point.row + 1,
                })

    except Exception as e:
        result["error"] = str(e)

    return result


def run_query_suite(code: str, queries: dict[str, str], suite_name: str) -> None:
    """Run a suite of queries and print results."""
    print(f"\n{'='*60}")
    print(f"  {suite_name}")
    print(f"{'='*60}")

    for query_name, query_text in queries.items():
        result = run_query(code, query_text, query_name)

        status = "OK" if result["success"] else "FAILED"
        print(f"\n[{status}] {query_name}")

        if result["error"]:
            print(f"  Error: {result['error']}")
        else:
            print(f"  Captures: {result['captures']}")
            print(f"  Total matches: {result['match_count']}")

            if result["captured_text"]:
                print("  Sample matches:")
                for match in result["captured_text"][:3]:
                    text = match['text'].replace('\n', '\\n')
                    if len(text) > 60:
                        text = text[:60] + "..."
                    print(f"    Line {match['line']}: @{match['capture']}: {text}")


def test_query_limitations():
    """Test and document query limitations."""
    print(f"\n{'='*60}")
    print("  QUERY LIMITATIONS & GOTCHAS")
    print(f"{'='*60}")

    limitations = []

    # Test 1: Negation patterns
    print("\n[TEST] Negation patterns (finding missing things)")
    try:
        # Try to find functions WITHOUT docstrings
        query_text = '''
        (function_definition
          body: (block
            . (expression_statement (string)) @has_doc)
        ) @func_with_doc
        '''
        tree = parser.parse(bytes(DOCSTRING_TEST_CODE, "utf-8"))
        query = Query(PY_LANGUAGE, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        print("  Can find functions WITH docstrings")
        print("  NOTE: Finding functions WITHOUT docstrings requires set difference")
        limitations.append("Cannot directly express 'does not contain' - need post-processing")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 2: Counting constraints
    print("\n[TEST] Counting constraints (e.g., more than N)")
    try:
        # Try to count return statements
        query_text = '''
        (function_definition
          body: (block
            (return_statement)+ @returns)
        ) @multi_return_func
        '''
        tree = parser.parse(bytes(CODE_SMELL_TEST_CODE, "utf-8"))
        query = Query(PY_LANGUAGE, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        print(f"  Found {len(captures.get('returns', []))} return statements")
        print("  NOTE: Cannot express 'more than N' in query - need post-processing")
        limitations.append("Cannot express counting constraints like 'more than 3 returns'")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 3: Cross-reference patterns
    print("\n[TEST] Cross-reference patterns (variable flow)")
    print("  NOTE: Cannot track data flow (e.g., user input -> eval)")
    print("  Tree-sitter is structural, not semantic")
    limitations.append("Cannot track data/control flow - structural matching only")

    # Test 4: Sibling ordering
    print("\n[TEST] Sibling ordering and position predicates")
    try:
        # First child predicate
        query_text = '''
        (block
          . (expression_statement (string) @first_string)
        )
        '''
        tree = parser.parse(bytes(DOCSTRING_TEST_CODE, "utf-8"))
        query = Query(PY_LANGUAGE, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        print(f"  First-child anchor (.) works: found {len(captures.get('first_string', []))} matches")
    except Exception as e:
        print(f"  Error: {e}")

    # Test 5: Regex limitations
    print("\n[TEST] Regex predicate limitations")
    try:
        # Test complex regex
        query_text = '''
        (string) @str
        (#match? @str "(?i)password")
        '''
        code = 'x = "MyPassword123"'
        tree = parser.parse(bytes(code, "utf-8"))
        query = Query(PY_LANGUAGE, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        print(f"  Case-insensitive regex works: {len(captures.get('str', []))} matches")
    except Exception as e:
        print(f"  Error with regex: {e}")
        limitations.append(f"Regex predicate issue: {e}")

    # Test 6: String content access
    print("\n[TEST] String content vs string node")
    try:
        query_text = '''
        (string
          (string_content) @content
        ) @full_string
        '''
        code = 'x = "hello world"'
        tree = parser.parse(bytes(code, "utf-8"))
        query = Query(PY_LANGUAGE, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        if captures.get('content'):
            node = captures['content'][0]
            print(f"  string_content node exists: '{code[node.start_byte:node.end_byte]}'")
        else:
            print("  string_content not captured - may need different structure")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n" + "-"*60)
    print("Summary of Limitations:")
    for i, lim in enumerate(limitations, 1):
        print(f"  {i}. {lim}")


def test_advanced_patterns():
    """Test more advanced/complex query patterns."""
    print(f"\n{'='*60}")
    print("  ADVANCED PATTERN TESTS")
    print(f"{'='*60}")

    # Test: Multiple alternatives
    print("\n[TEST] Multiple alternatives in patterns")
    query_text = '''
    ; Match dangerous functions
    (call
      function: [
        (identifier) @func_id
        (attribute attribute: (identifier) @attr_id)
      ]
      (#match? @func_id "^(eval|exec)$")?
      (#match? @attr_id "^(system|call|run)$")?
    ) @dangerous_call
    '''

    code = '''
eval(x)
os.system("ls")
subprocess.run(cmd)
safe_function()
'''
    result = run_query(code, query_text, "multiple_alternatives")
    print(f"  Success: {result['success']}")
    if result['error']:
        print(f"  Error: {result['error']}")
    else:
        print(f"  Matches: {result['match_count']}")

    # Test: Quantifiers
    print("\n[TEST] Quantifiers (+, *, ?)")
    query_text = '''
    (import_from_statement
      name: (dotted_name)+ @imported_names
    )
    '''

    result = run_query(IMPORT_TEST_CODE, query_text, "quantifiers")
    print(f"  Success: {result['success']}")
    print(f"  Matches: {result['match_count'] if result['success'] else 'N/A'}")

    # Test: Field names
    print("\n[TEST] Field name access")
    query_text = '''
    (function_definition
      name: (identifier) @name
      parameters: (parameters) @params
      return_type: (type)? @return_type
      body: (block) @body
    ) @func
    '''

    code = '''
def typed_func(x: int, y: str) -> bool:
    return True

def untyped_func(x, y):
    return False
'''
    result = run_query(code, query_text, "field_access")
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Captures: {result['captures']}")


def main():
    """Run all query tests."""
    print("Tree-sitter Query Pattern Capability Test")
    print("=" * 60)
    print(f"Tree-sitter Python language initialized: {PY_LANGUAGE}")

    # Run query suites
    run_query_suite(SECURITY_TEST_CODE, SECURITY_QUERIES, "SECURITY PATTERN DETECTION")
    run_query_suite(CODE_SMELL_TEST_CODE, CODE_SMELL_QUERIES, "CODE SMELL DETECTION")
    run_query_suite(DOCSTRING_TEST_CODE, DOCSTRING_QUERIES, "DOCSTRING EXTRACTION")
    run_query_suite(IMPORT_TEST_CODE, IMPORT_QUERIES, "IMPORT ANALYSIS")

    # Test limitations
    test_query_limitations()

    # Test advanced patterns
    test_advanced_patterns()

    # Summary
    print(f"\n{'='*60}")
    print("  SUMMARY & RECOMMENDATIONS")
    print(f"{'='*60}")
    print("""
WORKS WELL:
- Structural pattern matching (function calls, class definitions)
- Regex matching on node text (#match? predicate)
- Field-based queries (name:, body:, etc.)
- First-child anchoring with '.' for docstrings
- Nested structure queries (if inside if inside if)
- Alternative patterns with [...]

DIFFICULT/IMPOSSIBLE:
- Data flow analysis (tracking variables across statements)
- Counting constraints ("more than N of X")
- Negation patterns ("function WITHOUT docstring")
- Cross-file analysis
- Semantic type information

GOTCHAS:
- Node type names must match grammar exactly
- String escaping in queries can be tricky
- Optional predicates (?) behavior varies
- Some predicates may not be supported in all versions

RECOMMENDATIONS FOR CODE AUDITING:
1. Use tree-sitter for structural patterns (good)
2. Combine with post-processing for counting/negation
3. Use separate tool for data flow analysis
4. Build a library of tested query patterns
5. Consider performance for large codebases
""")


if __name__ == "__main__":
    main()
