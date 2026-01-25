#!/usr/bin/env python3
"""
Tree-sitter based complexity analysis for Python and TypeScript.

This script implements:
- Cyclomatic complexity calculation
- Cognitive complexity calculation
- Maximum nesting depth calculation
- Code smell detection
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import tree_sitter_python as ts_python
import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Node, Parser


# ==============================================================================
# Configuration
# ==============================================================================

PY_LANGUAGE = Language(ts_python.language())
TS_LANGUAGE = Language(ts_typescript.language_typescript())

# Thresholds for code smells
MAX_CYCLOMATIC_COMPLEXITY = 10
MAX_COGNITIVE_COMPLEXITY = 15
MAX_NESTING_DEPTH = 4
MAX_FUNCTION_LINES = 50
MAX_PARAMETERS = 5


# ==============================================================================
# Data Classes
# ==============================================================================

@dataclass
class FunctionMetrics:
    """Metrics for a single function."""
    name: str
    start_line: int
    end_line: int
    cyclomatic_complexity: int = 1  # Base complexity
    cognitive_complexity: int = 0
    max_nesting_depth: int = 0
    parameter_count: int = 0
    line_count: int = 0
    code_smells: list = field(default_factory=list)

    def __post_init__(self):
        self.line_count = self.end_line - self.start_line + 1

    def detect_smells(self):
        """Detect code smells based on metrics."""
        self.code_smells = []

        if self.cyclomatic_complexity > MAX_CYCLOMATIC_COMPLEXITY:
            self.code_smells.append(
                f"High cyclomatic complexity: {self.cyclomatic_complexity} "
                f"(threshold: {MAX_CYCLOMATIC_COMPLEXITY})"
            )

        if self.cognitive_complexity > MAX_COGNITIVE_COMPLEXITY:
            self.code_smells.append(
                f"High cognitive complexity: {self.cognitive_complexity} "
                f"(threshold: {MAX_COGNITIVE_COMPLEXITY})"
            )

        if self.max_nesting_depth > MAX_NESTING_DEPTH:
            self.code_smells.append(
                f"Deep nesting: {self.max_nesting_depth} levels "
                f"(threshold: {MAX_NESTING_DEPTH})"
            )

        if self.line_count > MAX_FUNCTION_LINES:
            self.code_smells.append(
                f"Long function: {self.line_count} lines "
                f"(threshold: {MAX_FUNCTION_LINES})"
            )

        if self.parameter_count > MAX_PARAMETERS:
            self.code_smells.append(
                f"Too many parameters: {self.parameter_count} "
                f"(threshold: {MAX_PARAMETERS})"
            )

    def complexity_rating(self) -> str:
        """Return a human-readable complexity rating."""
        # Combined score based on both metrics
        avg = (self.cyclomatic_complexity + self.cognitive_complexity) / 2

        if avg <= 3:
            return "LOW"
        elif avg <= 8:
            return "MEDIUM"
        elif avg <= 15:
            return "HIGH"
        else:
            return "VERY HIGH"


@dataclass
class FileAnalysis:
    """Analysis results for a file."""
    filepath: str
    language: str
    functions: list = field(default_factory=list)
    total_lines: int = 0
    parse_errors: list = field(default_factory=list)


# ==============================================================================
# Language-Specific Configuration
# ==============================================================================

# Python decision point node types
PYTHON_DECISION_POINTS = {
    "if_statement",
    "elif_clause",
    "for_statement",
    "while_statement",
    "except_clause",
    "with_statement",
    "boolean_operator",  # and/or
    "conditional_expression",  # ternary
    "list_comprehension",
    "dictionary_comprehension",
    "set_comprehension",
    "generator_expression",
}

# Python nesting increment node types
PYTHON_NESTING_NODES = {
    "if_statement",
    "for_statement",
    "while_statement",
    "try_statement",
    "with_statement",
    "function_definition",
    "class_definition",
}

# TypeScript decision point node types
TS_DECISION_POINTS = {
    "if_statement",
    "for_statement",
    "for_in_statement",
    "while_statement",
    "do_statement",
    "switch_case",
    "catch_clause",
    "binary_expression",  # Will check for && and ||
    "ternary_expression",
}

# TypeScript nesting increment node types
TS_NESTING_NODES = {
    "if_statement",
    "for_statement",
    "for_in_statement",
    "while_statement",
    "do_statement",
    "try_statement",
    "switch_statement",
    "function_declaration",
    "method_definition",
    "arrow_function",
    "class_declaration",
}


# ==============================================================================
# Complexity Calculators
# ==============================================================================

class PythonComplexityAnalyzer:
    """Analyzes complexity of Python code."""

    def __init__(self, source_code: bytes):
        self.source = source_code
        self.parser = Parser(PY_LANGUAGE)
        self.tree = self.parser.parse(source_code)

    def find_functions(self) -> list[tuple[Node, str]]:
        """Find all function definitions in the code."""
        functions = []
        self._find_functions_recursive(self.tree.root_node, functions)
        return functions

    def _find_functions_recursive(self, node: Node, functions: list):
        """Recursively find function definitions."""
        if node.type == "function_definition":
            # Get function name
            name_node = node.child_by_field_name("name")
            if name_node:
                name = self.source[name_node.start_byte:name_node.end_byte].decode()
                functions.append((node, name))

        for child in node.children:
            self._find_functions_recursive(child, functions)

    def count_parameters(self, func_node: Node) -> int:
        """Count the number of parameters in a function."""
        params_node = func_node.child_by_field_name("parameters")
        if not params_node:
            return 0

        count = 0
        for child in params_node.children:
            if child.type in ("identifier", "typed_parameter", "default_parameter",
                              "typed_default_parameter", "list_splat_pattern",
                              "dictionary_splat_pattern"):
                count += 1
        return count

    def calculate_cyclomatic(self, node: Node) -> int:
        """Calculate cyclomatic complexity for a node."""
        complexity = 1  # Base complexity

        def traverse(n: Node):
            nonlocal complexity

            if n.type in PYTHON_DECISION_POINTS:
                # Special handling for boolean operators
                if n.type == "boolean_operator":
                    complexity += 1
                else:
                    complexity += 1

            for child in n.children:
                traverse(child)

        traverse(node)
        return complexity

    def calculate_cognitive(self, node: Node) -> int:
        """
        Calculate cognitive complexity.

        Cognitive complexity accounts for:
        1. Structural increments (control flow)
        2. Nesting penalty (deeper nesting = harder to understand)
        3. Increments for breaks in linear flow
        """
        cognitive = 0

        def traverse(n: Node, nesting_level: int):
            nonlocal cognitive

            # Increment for structural nodes
            structural_increment = 0
            nesting_increment = 0

            if n.type in ("if_statement", "elif_clause"):
                structural_increment = 1
                nesting_increment = nesting_level
            elif n.type in ("for_statement", "while_statement"):
                structural_increment = 1
                nesting_increment = nesting_level
            elif n.type == "except_clause":
                structural_increment = 1
                nesting_increment = nesting_level
            elif n.type == "boolean_operator":
                # Each sequence of same operators counts as one
                structural_increment = 1
            elif n.type == "conditional_expression":
                structural_increment = 1
                nesting_increment = nesting_level
            elif n.type == "else_clause":
                structural_increment = 1

            cognitive += structural_increment + nesting_increment

            # Determine new nesting level
            new_nesting = nesting_level
            if n.type in ("if_statement", "for_statement", "while_statement",
                          "try_statement", "with_statement"):
                new_nesting = nesting_level + 1

            for child in n.children:
                traverse(child, new_nesting)

        traverse(node, 0)
        return cognitive

    def calculate_max_nesting(self, node: Node) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0

        def traverse(n: Node, current_depth: int):
            nonlocal max_depth

            # Check if this node increases nesting
            increases_nesting = n.type in PYTHON_NESTING_NODES

            new_depth = current_depth + (1 if increases_nesting else 0)
            max_depth = max(max_depth, new_depth)

            for child in n.children:
                traverse(child, new_depth)

        traverse(node, 0)
        return max_depth

    def analyze(self) -> FileAnalysis:
        """Perform full analysis of the Python file."""
        analysis = FileAnalysis(
            filepath="",
            language="Python",
            total_lines=len(self.source.decode().splitlines())
        )

        for func_node, func_name in self.find_functions():
            metrics = FunctionMetrics(
                name=func_name,
                start_line=func_node.start_point[0] + 1,
                end_line=func_node.end_point[0] + 1,
                parameter_count=self.count_parameters(func_node),
            )

            metrics.cyclomatic_complexity = self.calculate_cyclomatic(func_node)
            metrics.cognitive_complexity = self.calculate_cognitive(func_node)
            metrics.max_nesting_depth = self.calculate_max_nesting(func_node)
            metrics.detect_smells()

            analysis.functions.append(metrics)

        return analysis


class TypeScriptComplexityAnalyzer:
    """Analyzes complexity of TypeScript code."""

    def __init__(self, source_code: bytes):
        self.source = source_code
        self.parser = Parser(TS_LANGUAGE)
        self.tree = self.parser.parse(source_code)

    def find_functions(self) -> list[tuple[Node, str]]:
        """Find all function definitions in the code."""
        functions = []
        self._find_functions_recursive(self.tree.root_node, functions, None)
        return functions

    def _find_functions_recursive(self, node: Node, functions: list, class_name: Optional[str]):
        """Recursively find function definitions."""
        current_class = class_name

        # Track class name
        if node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                current_class = self.source[name_node.start_byte:name_node.end_byte].decode()

        # Function declarations
        if node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = self.source[name_node.start_byte:name_node.end_byte].decode()
                functions.append((node, name))

        # Arrow functions assigned to variables
        elif node.type == "lexical_declaration":
            for child in node.children:
                if child.type == "variable_declarator":
                    name_node = child.child_by_field_name("name")
                    value_node = child.child_by_field_name("value")
                    if name_node and value_node and value_node.type == "arrow_function":
                        name = self.source[name_node.start_byte:name_node.end_byte].decode()
                        functions.append((value_node, name))

        # Method definitions
        elif node.type == "method_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = self.source[name_node.start_byte:name_node.end_byte].decode()
                if current_class:
                    name = f"{current_class}.{name}"
                functions.append((node, name))

        for child in node.children:
            self._find_functions_recursive(child, functions, current_class)

    def count_parameters(self, func_node: Node) -> int:
        """Count the number of parameters in a function."""
        params_node = func_node.child_by_field_name("parameters")
        if not params_node:
            # Try finding formal_parameters for arrow functions
            for child in func_node.children:
                if child.type == "formal_parameters":
                    params_node = child
                    break

        if not params_node:
            return 0

        count = 0
        for child in params_node.children:
            if child.type in ("required_parameter", "optional_parameter",
                              "rest_parameter", "identifier"):
                count += 1
        return count

    def calculate_cyclomatic(self, node: Node) -> int:
        """Calculate cyclomatic complexity for a node."""
        complexity = 1  # Base complexity

        def traverse(n: Node):
            nonlocal complexity

            if n.type in TS_DECISION_POINTS:
                if n.type == "binary_expression":
                    # Only count && and ||
                    op_node = n.child_by_field_name("operator")
                    if op_node:
                        op = self.source[op_node.start_byte:op_node.end_byte].decode()
                        if op in ("&&", "||"):
                            complexity += 1
                else:
                    complexity += 1

            for child in n.children:
                traverse(child)

        traverse(node)
        return complexity

    def calculate_cognitive(self, node: Node) -> int:
        """Calculate cognitive complexity."""
        cognitive = 0

        def traverse(n: Node, nesting_level: int):
            nonlocal cognitive

            structural_increment = 0
            nesting_increment = 0

            if n.type == "if_statement":
                structural_increment = 1
                nesting_increment = nesting_level
            elif n.type in ("for_statement", "for_in_statement", "while_statement", "do_statement"):
                structural_increment = 1
                nesting_increment = nesting_level
            elif n.type == "catch_clause":
                structural_increment = 1
                nesting_increment = nesting_level
            elif n.type == "switch_case":
                structural_increment = 1
            elif n.type == "binary_expression":
                op_node = n.child_by_field_name("operator")
                if op_node:
                    op = self.source[op_node.start_byte:op_node.end_byte].decode()
                    if op in ("&&", "||"):
                        structural_increment = 1
            elif n.type == "ternary_expression":
                structural_increment = 1
                nesting_increment = nesting_level
            elif n.type == "else_clause":
                structural_increment = 1

            cognitive += structural_increment + nesting_increment

            # Determine new nesting level
            new_nesting = nesting_level
            if n.type in ("if_statement", "for_statement", "for_in_statement",
                          "while_statement", "do_statement", "try_statement",
                          "switch_statement"):
                new_nesting = nesting_level + 1

            for child in n.children:
                traverse(child, new_nesting)

        traverse(node, 0)
        return cognitive

    def calculate_max_nesting(self, node: Node) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0

        def traverse(n: Node, current_depth: int):
            nonlocal max_depth

            increases_nesting = n.type in TS_NESTING_NODES

            new_depth = current_depth + (1 if increases_nesting else 0)
            max_depth = max(max_depth, new_depth)

            for child in n.children:
                traverse(child, new_depth)

        traverse(node, 0)
        return max_depth

    def analyze(self) -> FileAnalysis:
        """Perform full analysis of the TypeScript file."""
        analysis = FileAnalysis(
            filepath="",
            language="TypeScript",
            total_lines=len(self.source.decode().splitlines())
        )

        for func_node, func_name in self.find_functions():
            metrics = FunctionMetrics(
                name=func_name,
                start_line=func_node.start_point[0] + 1,
                end_line=func_node.end_point[0] + 1,
                parameter_count=self.count_parameters(func_node),
            )

            metrics.cyclomatic_complexity = self.calculate_cyclomatic(func_node)
            metrics.cognitive_complexity = self.calculate_cognitive(func_node)
            metrics.max_nesting_depth = self.calculate_max_nesting(func_node)
            metrics.detect_smells()

            analysis.functions.append(metrics)

        return analysis


# ==============================================================================
# Reporting
# ==============================================================================

def print_analysis_report(analysis: FileAnalysis, filepath: str):
    """Print a formatted analysis report."""
    print("\n" + "=" * 80)
    print(f"COMPLEXITY ANALYSIS: {filepath}")
    print(f"Language: {analysis.language} | Total Lines: {analysis.total_lines}")
    print("=" * 80)

    if not analysis.functions:
        print("No functions found.")
        return

    # Print header
    print(f"\n{'Function':<40} {'CC':>4} {'CogC':>5} {'Nest':>5} {'Params':>6} {'Lines':>6} {'Rating':<10}")
    print("-" * 80)

    all_smells = []

    for func in analysis.functions:
        print(f"{func.name:<40} {func.cyclomatic_complexity:>4} {func.cognitive_complexity:>5} "
              f"{func.max_nesting_depth:>5} {func.parameter_count:>6} {func.line_count:>6} "
              f"{func.complexity_rating():<10}")

        if func.code_smells:
            for smell in func.code_smells:
                all_smells.append((func.name, smell))

    # Print code smells section
    if all_smells:
        print("\n" + "-" * 80)
        print("CODE SMELLS DETECTED:")
        print("-" * 80)
        for func_name, smell in all_smells:
            print(f"  [{func_name}] {smell}")

    # Summary statistics
    print("\n" + "-" * 80)
    print("SUMMARY:")
    print("-" * 80)

    avg_cc = sum(f.cyclomatic_complexity for f in analysis.functions) / len(analysis.functions)
    avg_cog = sum(f.cognitive_complexity for f in analysis.functions) / len(analysis.functions)
    max_cc = max(f.cyclomatic_complexity for f in analysis.functions)
    max_cog = max(f.cognitive_complexity for f in analysis.functions)

    print(f"  Functions analyzed: {len(analysis.functions)}")
    print(f"  Average cyclomatic complexity: {avg_cc:.1f}")
    print(f"  Average cognitive complexity: {avg_cog:.1f}")
    print(f"  Max cyclomatic complexity: {max_cc}")
    print(f"  Max cognitive complexity: {max_cog}")
    print(f"  Functions with code smells: {len(set(f for f, _ in all_smells))}")


def validate_expectations(analysis: FileAnalysis) -> list[tuple[str, bool, str]]:
    """Validate that complexity ratings match expectations."""
    expectations = {
        # Python functions
        "simple_function": ("LOW", "Simple single-line function"),
        "medium_complexity_function": ("MEDIUM", "Loop with conditionals"),
        "high_complexity_function": ("HIGH", "Deeply nested conditionals"),
        "function_with_many_params": ("LOW", "Simple but many parameters"),
        "execute_query": ("HIGH", "Complex retry logic with nesting"),

        # TypeScript functions
        "simpleFunction": ("LOW", "Simple single-line function"),
        "mediumComplexity": ("MEDIUM", "Loop with conditionals"),
        "functionWithManyParams": ("LOW", "Simple but many parameters"),
        "ConnectionManager.processData": ("HIGH", "Deeply nested type checking"),
        "arrowSimple": ("LOW", "Simple arrow function"),
        "arrowComplex": ("MEDIUM", "Arrow with filter and conditional"),
    }

    results = []

    for func in analysis.functions:
        if func.name in expectations:
            expected_rating, description = expectations[func.name]
            actual_rating = func.complexity_rating()

            # Allow some flexibility - adjacent ratings are acceptable
            rating_order = ["LOW", "MEDIUM", "HIGH", "VERY HIGH"]
            expected_idx = rating_order.index(expected_rating)
            actual_idx = rating_order.index(actual_rating)

            # Consider it a match if within 1 level
            is_match = abs(expected_idx - actual_idx) <= 1

            results.append((
                func.name,
                is_match,
                f"Expected: {expected_rating}, Got: {actual_rating} - {description}"
            ))

    return results


# ==============================================================================
# Main
# ==============================================================================

def main():
    """Main entry point."""
    base_path = Path("/home/blake/Development/AI-Prompt-Guide/tree-sitter-tests")

    python_file = base_path / "sample_python.py"
    typescript_file = base_path / "sample_typescript.ts"

    all_validations = []

    # Analyze Python file
    print("\n" + "#" * 80)
    print("# PYTHON ANALYSIS")
    print("#" * 80)

    with open(python_file, "rb") as f:
        python_source = f.read()

    py_analyzer = PythonComplexityAnalyzer(python_source)
    py_analysis = py_analyzer.analyze()
    print_analysis_report(py_analysis, str(python_file))
    all_validations.extend(validate_expectations(py_analysis))

    # Analyze TypeScript file
    print("\n" + "#" * 80)
    print("# TYPESCRIPT ANALYSIS")
    print("#" * 80)

    with open(typescript_file, "rb") as f:
        ts_source = f.read()

    ts_analyzer = TypeScriptComplexityAnalyzer(ts_source)
    ts_analysis = ts_analyzer.analyze()
    print_analysis_report(ts_analysis, str(typescript_file))
    all_validations.extend(validate_expectations(ts_analysis))

    # Validation results
    print("\n" + "#" * 80)
    print("# EXPECTATION VALIDATION")
    print("#" * 80)
    print()

    passed = 0
    failed = 0

    for func_name, is_match, description in all_validations:
        status = "PASS" if is_match else "FAIL"
        symbol = "[+]" if is_match else "[-]"
        print(f"  {symbol} {func_name}: {status}")
        print(f"      {description}")

        if is_match:
            passed += 1
        else:
            failed += 1

    print()
    print(f"  Validation Results: {passed} passed, {failed} failed")

    # Assessment for code review automation
    print("\n" + "#" * 80)
    print("# ASSESSMENT FOR CODE REVIEW AUTOMATION")
    print("#" * 80)
    print("""
USEFULNESS ASSESSMENT:

1. STRENGTHS:
   - Tree-sitter provides accurate, language-aware parsing
   - Fast parsing even for large files
   - Can handle both Python and TypeScript with same approach
   - Identifies complex functions that warrant human review
   - Code smell detection catches common anti-patterns

2. LIMITATIONS:
   - Cognitive complexity heuristics are approximations
   - Cannot detect semantic complexity (complex business logic)
   - Doesn't understand function purpose or domain complexity
   - May flag legitimate complex algorithms as problematic
   - Doesn't track inter-function dependencies

3. RECOMMENDATIONS FOR CODE REVIEW AUTOMATION:
   - Use as a pre-filter to flag files/functions needing attention
   - Combine with other metrics (test coverage, change frequency)
   - Set thresholds appropriate to your codebase
   - Use trends over time rather than absolute values
   - Always require human judgment for final decisions

4. INTEGRATION SUGGESTIONS:
   - CI/CD gate: Warn on complexity > threshold
   - PR comments: Auto-annotate complex functions
   - Dashboard: Track complexity trends across codebase
   - IDE plugin: Real-time feedback during development
""")


if __name__ == "__main__":
    main()
