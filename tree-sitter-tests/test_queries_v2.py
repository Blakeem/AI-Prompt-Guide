#!/usr/bin/env python3
"""
Tree-sitter Query Pattern Investigation - Part 2

Investigating failed patterns and exploring alternatives.
"""

import tree_sitter_python as ts_python
from tree_sitter import Language, Parser, Query, QueryCursor

# Initialize
PY_LANGUAGE = Language(ts_python.language())
parser = Parser(PY_LANGUAGE)


def show_tree(code: str, max_depth: int = 10):
    """Print the AST structure to understand node types."""
    tree = parser.parse(bytes(code, "utf-8"))

    def print_node(node, indent=0):
        if indent > max_depth:
            return
        text = code[node.start_byte:node.end_byte]
        if len(text) > 50:
            text = text[:50] + "..."
        text = text.replace('\n', '\\n')
        print(f"{'  ' * indent}{node.type} [{node.start_point.row}:{node.start_point.column}] = {text!r}")
        for child in node.children:
            print_node(child, indent + 1)

    print_node(tree.root_node)


def test_query(code: str, query_text: str, name: str):
    """Test a query and show results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print("-" * 60)

    try:
        tree = parser.parse(bytes(code, "utf-8"))
        query = Query(PY_LANGUAGE, query_text)
        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        print(f"SUCCESS - Captures: {list(captures.keys())}")
        for cap_name, nodes in captures.items():
            print(f"\n  @{cap_name} ({len(nodes)} matches):")
            for node in nodes[:3]:
                text = code[node.start_byte:node.end_byte]
                if len(text) > 60:
                    text = text[:60] + "..."
                text = text.replace('\n', '\\n')
                print(f"    Line {node.start_point.row + 1}: {text}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False


# =============================================================================
# Test 1: Understand nested ternary structure
# =============================================================================
print("\n" + "=" * 70)
print("INVESTIGATION: Nested Ternary Structure")
print("=" * 70)

ternary_code = '''
result = "a" if x > 0 else ("b" if y > 0 else "c")
simple = a if b else c
'''

print("\nAST Structure for nested ternary:")
show_tree(ternary_code, max_depth=8)

# Try different patterns for nested ternary
test_query(ternary_code, '''
; Find all conditional expressions
(conditional_expression) @ternary
''', "All conditional expressions")

test_query(ternary_code, '''
; Find conditional expressions that contain another conditional expression
(conditional_expression
  (conditional_expression) @inner
) @outer
''', "Nested conditional (child anywhere)")

test_query(ternary_code, '''
; Conditional with parenthesized alternative containing conditional
(conditional_expression
  alternative: (parenthesized_expression
    (conditional_expression) @inner
  )
) @outer
''', "Nested ternary via parenthesized_expression")


# =============================================================================
# Test 2: Understand except clause structure
# =============================================================================
print("\n" + "=" * 70)
print("INVESTIGATION: Except Clause Structure")
print("=" * 70)

except_code = '''
try:
    risky()
except:
    pass

try:
    other()
except Exception as e:
    handle(e)
'''

print("\nAST Structure for except clauses:")
show_tree(except_code, max_depth=8)

# Try different patterns
test_query(except_code, '''
; Find all except clauses
(except_clause) @except
''', "All except clauses")

test_query(except_code, '''
; Find except clauses with a type
(except_clause
  type: (_) @exc_type
) @typed_except
''', "Except with type")

test_query(except_code, '''
; Find except clauses that have a block with pass
(except_clause
  (block
    (pass_statement) @pass_stmt
  )
) @except_with_pass
''', "Except containing pass")

test_query(except_code, '''
; Bare except - try without field negation
(except_clause) @bare_except
''', "All except (need post-filter for bare)")


# =============================================================================
# Test 3: F-string SQL injection detection
# =============================================================================
print("\n" + "=" * 70)
print("INVESTIGATION: F-string SQL Detection")
print("=" * 70)

fstring_code = '''
query = f"SELECT * FROM users WHERE id = {user_id}"
safe = f"Hello {name}"
sql = f"DELETE FROM {table} WHERE x = 1"
'''

print("\nAST Structure for f-strings:")
show_tree(fstring_code, max_depth=6)

test_query(fstring_code, '''
; Find f-strings
(string
  (string_start) @start
  (#match? @start "^[fF]")
) @fstring
''', "F-strings by prefix")

test_query(fstring_code, '''
; Find strings with interpolation containing SQL keywords
(string
  (interpolation) @interp
) @string_with_interp
''', "Strings with interpolation")


# =============================================================================
# Test 4: Magic numbers detection
# =============================================================================
print("\n" + "=" * 70)
print("INVESTIGATION: Magic Numbers")
print("=" * 70)

magic_code = '''
x = 42
y = 3.14159
if count > 100:
    timeout = 30000
PI = 3.14159  # Named constant is OK
'''

print("\nAST Structure for numbers:")
show_tree(magic_code, max_depth=5)

test_query(magic_code, '''
; Find integer literals in comparisons
(comparison_operator
  (integer) @magic_int
)
''', "Integers in comparisons")

test_query(magic_code, '''
; Find all integer literals not in constant assignment
(integer) @number
''', "All integers")


# =============================================================================
# Test 5: Try detecting assertion patterns
# =============================================================================
print("\n" + "=" * 70)
print("INVESTIGATION: Assert Statements")
print("=" * 70)

assert_code = '''
assert x > 0, "x must be positive"
assert condition
assert a == b, f"Expected {a} to equal {b}"
'''

print("\nAST Structure for assert:")
show_tree(assert_code, max_depth=5)

test_query(assert_code, '''
; Find assert statements
(assert_statement
  condition: (_) @condition
  message: (_)? @message
) @assert
''', "Assert with optional message")


# =============================================================================
# Test 6: Class method detection (self parameter)
# =============================================================================
print("\n" + "=" * 70)
print("INVESTIGATION: Instance vs Class vs Static Methods")
print("=" * 70)

method_code = '''
class MyClass:
    def instance_method(self, x):
        pass

    @classmethod
    def class_method(cls, x):
        pass

    @staticmethod
    def static_method(x):
        pass

    def another_instance(self):
        pass
'''

print("\nAST Structure for methods:")
show_tree(method_code, max_depth=7)

test_query(method_code, '''
; Find methods with self parameter
(function_definition
  parameters: (parameters
    . (identifier) @first_param
    (#eq? @first_param "self")
  )
) @instance_method
''', "Methods with self first param")

test_query(method_code, '''
; Find methods with classmethod decorator
(decorated_definition
  (decorator
    (identifier) @dec_name
    (#eq? @dec_name "classmethod")
  )
  definition: (function_definition) @class_method
)
''', "Classmethod decorated functions")

test_query(method_code, '''
; Find staticmethod decorated
(decorated_definition
  (decorator
    (identifier) @dec_name
    (#eq? @dec_name "staticmethod")
  )
  definition: (function_definition) @static_method
)
''', "Staticmethod decorated functions")


# =============================================================================
# Test 7: Comprehension complexity
# =============================================================================
print("\n" + "=" * 70)
print("INVESTIGATION: Nested Comprehensions")
print("=" * 70)

comp_code = '''
simple = [x for x in items]
nested = [[x for x in row] for row in matrix]
with_if = [x for x in items if x > 0 if x < 100]
dict_comp = {k: v for k, v in items.items()}
'''

print("\nAST Structure for comprehensions:")
show_tree(comp_code, max_depth=6)

test_query(comp_code, '''
; Find list comprehensions containing list comprehensions
(list_comprehension
  body: (list_comprehension) @inner
) @nested_comp
''', "Nested list comprehensions")

test_query(comp_code, '''
; Find comprehensions with multiple if clauses
(list_comprehension
  (if_clause) @if1
  (if_clause) @if2
) @multi_if_comp
''', "Comprehensions with multiple if clauses")


# =============================================================================
# Summary of findings
# =============================================================================
print("\n" + "=" * 70)
print("FINDINGS SUMMARY")
print("=" * 70)
print("""
KEY DISCOVERIES:

1. NESTED TERNARY:
   - The nested conditional IS wrapped in parenthesized_expression
   - Query: (conditional_expression alternative: (parenthesized_expression (conditional_expression)))
   - WORKS with explicit parenthesized_expression node

2. EXCEPT CLAUSE:
   - Bare except has no 'type' field, typed except has type field
   - Cannot use field negation (!type) directly in all cases
   - Solution: Query all except clauses, post-filter in Python

3. F-STRINGS:
   - Have 'interpolation' child nodes
   - string_start shows the prefix (f", F', etc.)
   - Can match SQL keywords in the string content

4. METHODS:
   - Can detect self/cls first parameter with anchored match
   - Can detect decorators by name
   - Good support for method classification

5. COMPREHENSIONS:
   - Nested comprehensions detectable
   - Multiple if clauses queryable
   - Good structural support

GENERAL PATTERNS THAT WORK:
- Field-anchored matches: parameters: (parameters . (identifier) @first)
- Equality predicates: (#eq? @name "value")
- Regex predicates: (#match? @name "pattern")
- Optional fields: field: (_)?
- Alternatives: [node_type1 node_type2]
- Quantifiers in some contexts: (_)+

PATTERNS THAT NEED WORKAROUNDS:
- Negation: Query positive case, subtract in post-processing
- Counting: Query all, count in post-processing
- Field absence: Sometimes works with !field, sometimes needs workaround
""")
