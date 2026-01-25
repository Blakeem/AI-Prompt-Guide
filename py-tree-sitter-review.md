# py-tree-sitter Evaluation for Claude Code Plugin

## Executive Summary

**Recommendation: Adopt for code analysis workflows**

py-tree-sitter is well-suited for Claude Code plugin integration, particularly for:
- **Complexity analysis** - Production-ready, highly accurate
- **Code smell detection** - Works well with query patterns
- **Security pattern scanning** - Good for structural patterns
- **Dead code detection** - Feasible but requires additional work

**Key Finding**: The library requires Python >= 3.10. For Python 3.13, use individual language packages (`tree-sitter-python`, `tree-sitter-typescript`) rather than `tree-sitter-languages` bundle.

---

## Installation (Python 3.13+)

```bash
pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript
```

The `tree-sitter-languages` bundle does not yet support Python 3.13.

---

## API Reference (v0.25.2)

The API has changed significantly from older versions. Here is the current correct usage:

```python
import tree_sitter_python as ts_python
import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Parser, Query, QueryCursor

# Create language objects
PY_LANGUAGE = Language(ts_python.language())
TS_LANGUAGE = Language(ts_typescript.language_typescript())  # .ts files
TSX_LANGUAGE = Language(ts_typescript.language_tsx())        # .tsx files

# Create parser
parser = Parser(PY_LANGUAGE)
tree = parser.parse(source_bytes)  # Must be bytes

# Query usage
query = Query(PY_LANGUAGE, query_text)
cursor = QueryCursor(query)
captures = cursor.captures(tree.root_node)  # Returns dict: {'name': [nodes]}
```

### API Changes from Older Versions

| Old API | New API (v0.25.2) |
|---------|-------------------|
| `language.query(text)` | `Query(language, text)` |
| `query.captures(node)` | `QueryCursor(query).captures(node)` |
| `cursor.current_field_name()` | `cursor.field_name` (property) |
| Returns list of tuples | Returns dict of capture_name -> [nodes] |

---

## Feature Testing Results

### 1. Basic Parsing and AST Traversal

**Status: Fully Working**

Both Python and TypeScript parsing work correctly. Key capabilities tested:

| Capability | Python | TypeScript | Notes |
|------------|--------|------------|-------|
| Function extraction | Pass | Pass | Includes arrow functions |
| Class extraction | Pass | Pass | Methods, properties, hierarchy |
| Import analysis | Pass | Pass | Named, aliased, star imports |
| Type annotations | Pass | Pass | Parameters, return types |
| Docstrings/JSDoc | Pass | Pass | First-child anchor pattern |

**Performance**: Sub-millisecond parsing for typical files. TreeCursor traversal is memory-efficient for large ASTs (1000+ nodes).

### 2. Complexity Analysis

**Status: Production Ready**

Tested complexity metrics against sample code with known complexity levels:

| Function | Expected | Cyclomatic | Cognitive | Nesting | Result |
|----------|----------|------------|-----------|---------|--------|
| `simple_function` | LOW | 1 | 0 | 1 | PASS |
| `medium_complexity_function` | MEDIUM | 4 | 7 | 3 | PASS |
| `high_complexity_function` | HIGH | 11 | 38 | 6 | PASS |
| `ConnectionManager.processData` | HIGH | 11 | 41 | 8 | PASS |

**All 11 validation checks passed.** The complexity ratings correctly identified functions that warrant review.

**Decision Point Counting** (for cyclomatic complexity):

| Language | Decision Point Nodes |
|----------|---------------------|
| Python | `if_statement`, `elif_clause`, `for_statement`, `while_statement`, `except_clause`, `conditional_expression`, `boolean_operator` |
| TypeScript | `if_statement`, `for_statement`, `for_in_statement`, `while_statement`, `do_statement`, `switch_case`, `catch_clause`, `ternary_expression` |

### 3. Query Pattern System

**Status: Highly Useful with Caveats**

31 query patterns tested successfully:

#### Security Patterns That Work

```python
# Detect eval/exec calls
EVAL_EXEC = '(call function: (identifier) @f (#match? @f "^(eval|exec)$"))'

# Detect subprocess with shell=True
SHELL_TRUE = '''
(call
  function: (attribute object: (identifier) @mod attribute: (identifier) @method)
  arguments: (argument_list
    (keyword_argument name: (identifier) @kw value: (true)))
  (#match? @mod "subprocess")
  (#eq? @kw "shell"))
'''

# Hardcoded secrets
HARDCODED_SECRET = '''
(assignment
  left: (identifier) @var
  right: (string) @value
  (#match? @var "(?i)(password|secret|api_key|token)"))
'''
```

#### Patterns That CANNOT Be Expressed

| Pattern | Reason | Workaround |
|---------|--------|------------|
| Data flow / taint tracking | Structural only, no semantics | Use CodeQL/Semgrep |
| Counting constraints (>N items) | No quantifier syntax | Post-process in Python |
| Negation (without docstring) | No negation in queries | Compute set difference |
| Type-aware analysis | No type inference | Integrate with type checkers |

### 4. Dead Code Detection

**Status: Feasible but Requires Additional Work**

| Metric | Result |
|--------|--------|
| True Positives | 75% (6/8 known dead code detected) |
| False Positives | ~21 items flagged incorrectly |
| False Negative Rate | 25% (2 missed) |

**What Was Detected Correctly**:
- `unused_function`, `_private_unused`, `UnusedClass`, `UNUSED_CONSTANT` (Python)
- `unusedInternalFunction`, `UNUSED_SECRET` (TypeScript)

**Limitations Discovered**:

| Limitation | Impact | Solution |
|------------|--------|----------|
| Magic methods (`__init__`) | False positives | Whitelist |
| Entry points (`main`) | False positives | Configuration |
| `self.method()` calls | False negatives | Build symbol table |
| Inherited methods | False negatives | Track class hierarchy |
| Dynamic calls (`getattr`) | Impossible | Accept limitation |

**Recommendation for Dead Code**: Start with module-level functions and constants (lower false positive rate), then expand to methods later.

---

## Recommended Workflow Integrations

### High-Value Use Cases

| Workflow | Capability | Confidence | Notes |
|----------|------------|------------|-------|
| **Code Review** | Complexity flagging | High | Auto-flag functions > threshold |
| **Code Audit** | Security pattern scan | Medium-High | Structural patterns only |
| **Refactoring** | Extract function candidates | High | Find long/complex functions |
| **Documentation** | Coverage analysis | High | Detect missing docstrings |
| **Import Analysis** | Unused import detection | High | Single-file analysis |

### Lower-Value / More Work Needed

| Workflow | Capability | Confidence | Notes |
|----------|------------|------------|-------|
| **Dead Code** | Unused function detection | Medium | High false positive rate |
| **Security Audit** | Taint analysis | Low | Not structural, need other tools |
| **Type Safety** | Type checking | None | Use mypy/tsc instead |

---

## Implementation Recommendations

### Skill: Code Complexity Audit

```python
# Recommended thresholds
MAX_CYCLOMATIC = 10     # Flag for review
MAX_COGNITIVE = 15       # Flag for refactoring
MAX_NESTING = 4          # Readability concern
MAX_PARAMS = 5           # Design smell
MAX_LINES = 50           # Candidate for extraction
```

Output format for skill:
```
## Complexity Report: src/module.py

### High Complexity Functions (Require Review)
| Function | Cyclomatic | Cognitive | Nesting | Issues |
|----------|------------|-----------|---------|--------|
| `execute_query` | 13 | 42 | 7 | Deep nesting, high complexity |
| `process_data` | 11 | 38 | 6 | Consider breaking into smaller functions |
```

### Skill: Security Pattern Scan

Query library for common security patterns:
- `eval()`/`exec()` usage
- `subprocess` with `shell=True`
- Hardcoded passwords/secrets
- SQL string concatenation
- Bare `except` clauses

### Skill: Dead Code Candidates

Two-tier approach:
1. **High confidence**: Module-level functions with no references in file or imports
2. **Medium confidence**: Class methods that appear unused (requires manual review)

---

## Test Files Created

All test files are in `/home/blake/Development/AI-Prompt-Guide/tree-sitter-tests/`:

| File | Purpose |
|------|---------|
| `sample_python.py` | Test file with varying complexity |
| `sample_typescript.ts` | TypeScript test file |
| `consumer_python.py` | Cross-file import test |
| `consumer_typescript.ts` | Cross-file import test |
| `test_python_parsing.py` | Python parsing tests |
| `test_typescript_parsing.py` | TypeScript parsing tests |
| `test_complexity.py` | Complexity analysis implementation |
| `test_dead_code.py` | Dead code detection tests |
| `test_queries_final.py` | Query pattern library (31 patterns) |

---

## Key Learnings

### What Works Well

1. **Structural pattern matching** - Query system is powerful for finding code patterns
2. **Complexity metrics** - Accurate, matches expectations
3. **Multi-language support** - Same concepts work across Python/TypeScript
4. **Performance** - Fast enough for interactive use
5. **Error tolerance** - Produces valid trees even with syntax errors

### What Requires Caution

1. **API instability** - Different between v0.22 and v0.25
2. **Dead code detection** - High false positive rate without additional logic
3. **Cross-file analysis** - Must build your own file index
4. **TypeScript vs TSX** - Must use correct parser for file type
5. **Query limitations** - No negation, no counting, no semantics

### Architectural Recommendation

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code Plugin                    │
├─────────────────────────────────────────────────────────┤
│ Tree-sitter Layer                                        │
│ ├── Parsing (instant)                                   │
│ ├── Query Patterns (security, smells)                   │
│ └── Complexity Calculation                              │
├─────────────────────────────────────────────────────────┤
│ Python Post-Processing                                   │
│ ├── Counting (> N returns, etc.)                        │
│ ├── Negation (functions WITHOUT docstrings)             │
│ ├── Cross-file index building                           │
│ └── False positive filtering                            │
├─────────────────────────────────────────────────────────┤
│ External Tools (when needed)                            │
│ ├── mypy/tsc for type checking                          │
│ ├── Semgrep/CodeQL for taint analysis                   │
│ └── vulture/knip for dead code validation               │
└─────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Create complexity skill** - Wrap test_complexity.py as `/audit-complexity` skill
2. **Create query pattern library** - Consolidate security/smell patterns from test_queries_final.py
3. **Prototype dead code skill** - Start with high-confidence module-level detection
4. **Document API patterns** - Create helper module for common operations
