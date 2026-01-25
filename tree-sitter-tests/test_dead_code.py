#!/usr/bin/env python3
"""
Dead Code Detection using Tree-sitter

This script explores tree-sitter's capabilities for detecting potentially unused code.
It analyzes both Python and TypeScript files to:
1. Extract all definitions (functions, classes, constants, types)
2. Extract all references/usages
3. Compare definitions vs usages within a file
4. Perform cross-file analysis for imports/exports

Known dead code in test files:
- Python: unused_function, _private_unused, UnusedClass, UNUSED_CONSTANT
- TypeScript: unusedInternalFunction, UnusedHelper, UNUSED_SECRET, UnusedType
"""

import tree_sitter_python as ts_python
import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Parser
from pathlib import Path
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional
from collections import defaultdict

# Initialize languages
PY_LANGUAGE = Language(ts_python.language())
TS_LANGUAGE = Language(ts_typescript.language_typescript())


@dataclass
class Definition:
    """Represents a code definition (function, class, constant, etc.)."""
    name: str
    kind: str  # 'function', 'class', 'constant', 'type', 'interface', 'method'
    line: int
    is_exported: bool = False
    is_private: bool = False
    parent_class: Optional[str] = None


@dataclass
class Reference:
    """Represents a reference to a symbol."""
    name: str
    line: int
    context: str  # 'call', 'instantiation', 'access', 'import', 'type_annotation'


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""
    file_path: str
    definitions: List[Definition] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    imports: Dict[str, str] = field(default_factory=dict)  # name -> source module
    exports: Set[str] = field(default_factory=set)


class PythonAnalyzer:
    """Analyzes Python files for definitions and references."""

    def __init__(self):
        self.parser = Parser(PY_LANGUAGE)

    def analyze(self, file_path: str) -> FileAnalysis:
        """Analyze a Python file."""
        source = Path(file_path).read_bytes()
        tree = self.parser.parse(source)

        analysis = FileAnalysis(file_path=file_path)

        self._extract_definitions(tree.root_node, source, analysis)
        self._extract_references(tree.root_node, source, analysis)
        self._extract_imports(tree.root_node, source, analysis)

        return analysis

    def _extract_definitions(self, node, source: bytes, analysis: FileAnalysis, parent_class: str = None):
        """Extract function, class, and constant definitions."""

        if node.type == 'function_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = source[name_node.start_byte:name_node.end_byte].decode()
                is_private = name.startswith('_')
                analysis.definitions.append(Definition(
                    name=name,
                    kind='method' if parent_class else 'function',
                    line=node.start_point[0] + 1,
                    is_private=is_private,
                    parent_class=parent_class
                ))

        elif node.type == 'class_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = source[name_node.start_byte:name_node.end_byte].decode()
                analysis.definitions.append(Definition(
                    name=name,
                    kind='class',
                    line=node.start_point[0] + 1
                ))
                # Recursively process class body for methods
                body = node.child_by_field_name('body')
                if body:
                    for child in body.children:
                        self._extract_definitions(child, source, analysis, parent_class=name)
                return  # Don't recurse normally for class

        elif node.type == 'expression_statement':
            # Look for constant assignments: NAME = value
            if len(node.children) > 0 and node.children[0].type == 'assignment':
                assign = node.children[0]
                left = assign.child_by_field_name('left')
                if left and left.type == 'identifier':
                    name = source[left.start_byte:left.end_byte].decode()
                    # Convention: UPPER_CASE = constant
                    if name.isupper() or '_' in name and name == name.upper():
                        analysis.definitions.append(Definition(
                            name=name,
                            kind='constant',
                            line=node.start_point[0] + 1
                        ))

        # Recurse for other nodes
        for child in node.children:
            if node.type != 'class_definition':  # Already handled
                self._extract_definitions(child, source, analysis, parent_class)

    def _extract_references(self, node, source: bytes, analysis: FileAnalysis):
        """Extract all symbol references."""

        if node.type == 'call':
            func = node.child_by_field_name('function')
            if func:
                if func.type == 'identifier':
                    name = source[func.start_byte:func.end_byte].decode()
                    analysis.references.append(Reference(
                        name=name,
                        line=node.start_point[0] + 1,
                        context='call'
                    ))
                elif func.type == 'attribute':
                    # Method call: obj.method()
                    attr = func.child_by_field_name('attribute')
                    if attr:
                        name = source[attr.start_byte:attr.end_byte].decode()
                        analysis.references.append(Reference(
                            name=name,
                            line=node.start_point[0] + 1,
                            context='call'
                        ))
                    # Also track the object being called on
                    obj = func.child_by_field_name('object')
                    if obj and obj.type == 'identifier':
                        name = source[obj.start_byte:obj.end_byte].decode()
                        analysis.references.append(Reference(
                            name=name,
                            line=node.start_point[0] + 1,
                            context='access'
                        ))

        elif node.type == 'identifier':
            # General identifier reference (variable access, type hints, etc.)
            parent = node.parent
            if parent and parent.type not in ('function_definition', 'class_definition',
                                               'import_from_statement', 'import_statement',
                                               'assignment', 'parameter'):
                name = source[node.start_byte:node.end_byte].decode()
                # Skip common built-ins
                if name not in ('None', 'True', 'False', 'self', 'cls'):
                    analysis.references.append(Reference(
                        name=name,
                        line=node.start_point[0] + 1,
                        context='access'
                    ))

        for child in node.children:
            self._extract_references(child, source, analysis)

    def _extract_imports(self, node, source: bytes, analysis: FileAnalysis):
        """Extract import statements."""

        if node.type == 'import_from_statement':
            # from module import name1, name2
            module_node = node.child_by_field_name('module_name')
            module = source[module_node.start_byte:module_node.end_byte].decode() if module_node else ''

            for child in node.children:
                if child.type == 'dotted_name' and child != module_node:
                    name = source[child.start_byte:child.end_byte].decode()
                    analysis.imports[name] = module
                elif child.type == 'aliased_import':
                    name_node = child.child_by_field_name('name')
                    if name_node:
                        name = source[name_node.start_byte:name_node.end_byte].decode()
                        analysis.imports[name] = module

        for child in node.children:
            self._extract_imports(child, source, analysis)


class TypeScriptAnalyzer:
    """Analyzes TypeScript files for definitions and references."""

    def __init__(self):
        self.parser = Parser(TS_LANGUAGE)

    def analyze(self, file_path: str) -> FileAnalysis:
        """Analyze a TypeScript file."""
        source = Path(file_path).read_bytes()
        tree = self.parser.parse(source)

        analysis = FileAnalysis(file_path=file_path)

        self._extract_definitions(tree.root_node, source, analysis)
        self._extract_references(tree.root_node, source, analysis)
        self._extract_imports(tree.root_node, source, analysis)

        return analysis

    def _is_exported(self, node) -> bool:
        """Check if a declaration is exported."""
        # Check if parent is export_statement
        if node.parent and node.parent.type == 'export_statement':
            return True
        # Check for export keyword in siblings
        if node.parent:
            for sibling in node.parent.children:
                if sibling.type == 'export':
                    return True
        return False

    def _extract_definitions(self, node, source: bytes, analysis: FileAnalysis, parent_class: str = None):
        """Extract function, class, constant, type, and interface definitions."""

        # Handle export statements - process the declaration inside
        if node.type == 'export_statement':
            for child in node.children:
                if child.type in ('function_declaration', 'class_declaration',
                                  'lexical_declaration', 'type_alias_declaration',
                                  'interface_declaration'):
                    self._extract_definitions(child, source, analysis, parent_class)
                    # Mark as exported
                    if analysis.definitions:
                        analysis.definitions[-1].is_exported = True
                        analysis.exports.add(analysis.definitions[-1].name)
            return

        if node.type == 'function_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = source[name_node.start_byte:name_node.end_byte].decode()
                analysis.definitions.append(Definition(
                    name=name,
                    kind='function',
                    line=node.start_point[0] + 1,
                    is_exported=self._is_exported(node)
                ))

        elif node.type == 'class_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = source[name_node.start_byte:name_node.end_byte].decode()
                analysis.definitions.append(Definition(
                    name=name,
                    kind='class',
                    line=node.start_point[0] + 1,
                    is_exported=self._is_exported(node)
                ))
                # Process class body for methods
                body = node.child_by_field_name('body')
                if body:
                    for child in body.children:
                        self._extract_definitions(child, source, analysis, parent_class=name)
                return

        elif node.type == 'method_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = source[name_node.start_byte:name_node.end_byte].decode()
                # Check for private modifier
                is_private = False
                for child in node.children:
                    if child.type == 'accessibility_modifier':
                        mod = source[child.start_byte:child.end_byte].decode()
                        is_private = mod == 'private'
                        break
                analysis.definitions.append(Definition(
                    name=name,
                    kind='method',
                    line=node.start_point[0] + 1,
                    is_private=is_private,
                    parent_class=parent_class
                ))

        elif node.type == 'lexical_declaration':
            # const/let declarations
            for child in node.children:
                if child.type == 'variable_declarator':
                    name_node = child.child_by_field_name('name')
                    if name_node and name_node.type == 'identifier':
                        name = source[name_node.start_byte:name_node.end_byte].decode()
                        # Check for arrow function
                        value = child.child_by_field_name('value')
                        kind = 'constant'
                        if value and value.type == 'arrow_function':
                            kind = 'function'
                        analysis.definitions.append(Definition(
                            name=name,
                            kind=kind,
                            line=node.start_point[0] + 1,
                            is_exported=self._is_exported(node)
                        ))

        elif node.type == 'type_alias_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = source[name_node.start_byte:name_node.end_byte].decode()
                analysis.definitions.append(Definition(
                    name=name,
                    kind='type',
                    line=node.start_point[0] + 1,
                    is_exported=self._is_exported(node)
                ))

        elif node.type == 'interface_declaration':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = source[name_node.start_byte:name_node.end_byte].decode()
                analysis.definitions.append(Definition(
                    name=name,
                    kind='interface',
                    line=node.start_point[0] + 1,
                    is_exported=self._is_exported(node)
                ))

        for child in node.children:
            if node.type not in ('class_declaration',):
                self._extract_definitions(child, source, analysis, parent_class)

    def _extract_references(self, node, source: bytes, analysis: FileAnalysis):
        """Extract all symbol references."""

        if node.type == 'call_expression':
            func = node.child_by_field_name('function')
            if func:
                if func.type == 'identifier':
                    name = source[func.start_byte:func.end_byte].decode()
                    analysis.references.append(Reference(
                        name=name,
                        line=node.start_point[0] + 1,
                        context='call'
                    ))
                elif func.type == 'member_expression':
                    prop = func.child_by_field_name('property')
                    if prop:
                        name = source[prop.start_byte:prop.end_byte].decode()
                        analysis.references.append(Reference(
                            name=name,
                            line=node.start_point[0] + 1,
                            context='call'
                        ))

        elif node.type == 'new_expression':
            # Class instantiation: new ClassName()
            constructor = node.child_by_field_name('constructor')
            if constructor and constructor.type == 'identifier':
                name = source[constructor.start_byte:constructor.end_byte].decode()
                analysis.references.append(Reference(
                    name=name,
                    line=node.start_point[0] + 1,
                    context='instantiation'
                ))

        elif node.type == 'type_identifier':
            # Type reference in type annotations
            name = source[node.start_byte:node.end_byte].decode()
            analysis.references.append(Reference(
                name=name,
                line=node.start_point[0] + 1,
                context='type_annotation'
            ))

        elif node.type == 'identifier':
            parent = node.parent
            # Avoid definition contexts
            if parent and parent.type not in ('function_declaration', 'class_declaration',
                                               'variable_declarator', 'import_specifier',
                                               'type_alias_declaration', 'interface_declaration',
                                               'method_definition', 'formal_parameters'):
                name = source[node.start_byte:node.end_byte].decode()
                if name not in ('undefined', 'null', 'true', 'false', 'this', 'super',
                               'console', 'process', 'require', 'module', 'exports'):
                    analysis.references.append(Reference(
                        name=name,
                        line=node.start_point[0] + 1,
                        context='access'
                    ))

        for child in node.children:
            self._extract_references(child, source, analysis)

    def _extract_imports(self, node, source: bytes, analysis: FileAnalysis):
        """Extract import statements."""

        if node.type == 'import_statement':
            # Find the source module
            for child in node.children:
                if child.type == 'string':
                    module = source[child.start_byte:child.end_byte].decode().strip('"\'')
                    # Find imported names
                    for c in node.children:
                        if c.type == 'import_clause':
                            self._extract_import_names(c, source, analysis, module)

        for child in node.children:
            self._extract_imports(child, source, analysis)

    def _extract_import_names(self, node, source: bytes, analysis: FileAnalysis, module: str):
        """Extract names from import clause."""
        if node.type == 'import_specifier':
            name_node = node.child_by_field_name('name')
            if name_node:
                name = source[name_node.start_byte:name_node.end_byte].decode()
                analysis.imports[name] = module
        elif node.type == 'identifier':
            # Default import
            name = source[node.start_byte:node.end_byte].decode()
            analysis.imports[name] = module

        for child in node.children:
            self._extract_import_names(child, source, analysis, module)


class DeadCodeDetector:
    """Detects potentially dead code across files."""

    def __init__(self):
        self.py_analyzer = PythonAnalyzer()
        self.ts_analyzer = TypeScriptAnalyzer()

    def analyze_single_file(self, file_path: str) -> Dict:
        """Analyze a single file for dead code."""
        if file_path.endswith('.py'):
            analysis = self.py_analyzer.analyze(file_path)
        elif file_path.endswith('.ts'):
            analysis = self.ts_analyzer.analyze(file_path)
        else:
            return {"error": f"Unsupported file type: {file_path}"}

        # Build reference sets
        referenced_names = {ref.name for ref in analysis.references}

        # Find definitions that aren't referenced
        dead_candidates = []
        for defn in analysis.definitions:
            if defn.name not in referenced_names:
                dead_candidates.append(defn)

        return {
            "file": file_path,
            "definitions": analysis.definitions,
            "references": analysis.references,
            "imports": analysis.imports,
            "dead_candidates": dead_candidates
        }

    def analyze_project(self, files: List[str]) -> Dict:
        """Analyze multiple files for cross-file dead code."""

        # Analyze all files
        analyses = {}
        for f in files:
            if f.endswith('.py'):
                analyses[f] = self.py_analyzer.analyze(f)
            elif f.endswith('.ts'):
                analyses[f] = self.ts_analyzer.analyze(f)

        # Build global reference index
        all_imports = defaultdict(set)  # symbol -> set of files that import it
        all_references = defaultdict(set)  # symbol -> set of files that reference it
        all_definitions = {}  # symbol -> (file, definition)

        for file_path, analysis in analyses.items():
            # Track imports
            for name, module in analysis.imports.items():
                all_imports[name].add(file_path)

            # Track references (excluding imports themselves)
            for ref in analysis.references:
                all_references[ref.name].add(file_path)

            # Track definitions
            for defn in analysis.definitions:
                key = f"{Path(file_path).stem}:{defn.name}"
                all_definitions[defn.name] = (file_path, defn)

        # Find unused definitions
        results = {
            "files_analyzed": len(files),
            "single_file_dead_code": {},
            "cross_file_dead_code": [],
            "exported_but_unused": [],
            "private_unused": [],
        }

        for file_path, analysis in analyses.items():
            # Single file analysis
            file_refs = {ref.name for ref in analysis.references}
            single_dead = []

            for defn in analysis.definitions:
                # Check if referenced in same file
                if defn.name not in file_refs:
                    # Check if it's imported elsewhere
                    if defn.name not in all_imports:
                        if defn.is_private or defn.name.startswith('_'):
                            results["private_unused"].append({
                                "file": file_path,
                                "name": defn.name,
                                "kind": defn.kind,
                                "line": defn.line
                            })
                        elif defn.is_exported or defn.kind in ('function', 'class', 'constant'):
                            # Potentially dead - not used locally or imported
                            results["exported_but_unused"].append({
                                "file": file_path,
                                "name": defn.name,
                                "kind": defn.kind,
                                "line": defn.line,
                                "is_exported": defn.is_exported
                            })
                        else:
                            single_dead.append({
                                "name": defn.name,
                                "kind": defn.kind,
                                "line": defn.line
                            })

            if single_dead:
                results["single_file_dead_code"][file_path] = single_dead

        return results


def print_analysis_results(results: Dict, title: str):
    """Pretty print analysis results."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

    if "error" in results:
        print(f"Error: {results['error']}")
        return

    if "definitions" in results:
        print(f"\n[Definitions Found] ({len(results['definitions'])})")
        for d in results['definitions']:
            exported = " [EXPORTED]" if d.is_exported else ""
            private = " [PRIVATE]" if d.is_private else ""
            parent = f" (in {d.parent_class})" if d.parent_class else ""
            print(f"  Line {d.line:3}: {d.kind:12} {d.name}{parent}{exported}{private}")

    if "dead_candidates" in results:
        print(f"\n[Dead Code Candidates] ({len(results['dead_candidates'])})")
        for d in results['dead_candidates']:
            print(f"  Line {d.line:3}: {d.kind:12} {d.name}")

    if "imports" in results and results["imports"]:
        print(f"\n[Imports] ({len(results['imports'])})")
        for name, module in results['imports'].items():
            print(f"  {name} from {module}")


def print_project_results(results: Dict):
    """Pretty print cross-file analysis results."""
    print(f"\n{'='*60}")
    print(" CROSS-FILE DEAD CODE ANALYSIS")
    print('='*60)

    print(f"\nFiles analyzed: {results['files_analyzed']}")

    if results["exported_but_unused"]:
        print(f"\n[Exported/Public but Potentially Unused] ({len(results['exported_but_unused'])})")
        for item in results["exported_but_unused"]:
            exported_marker = " (exported)" if item.get('is_exported') else ""
            print(f"  {Path(item['file']).name} line {item['line']:3}: "
                  f"{item['kind']:12} {item['name']}{exported_marker}")

    if results["private_unused"]:
        print(f"\n[Private/Internal Unused] ({len(results['private_unused'])})")
        for item in results["private_unused"]:
            print(f"  {Path(item['file']).name} line {item['line']:3}: "
                  f"{item['kind']:12} {item['name']}")

    if results["single_file_dead_code"]:
        print(f"\n[Single File Dead Code]")
        for file_path, items in results["single_file_dead_code"].items():
            print(f"  {Path(file_path).name}:")
            for item in items:
                print(f"    Line {item['line']:3}: {item['kind']:12} {item['name']}")


def main():
    """Run dead code detection analysis."""

    base_dir = Path("/home/blake/Development/AI-Prompt-Guide/tree-sitter-tests")

    detector = DeadCodeDetector()

    # Known dead code for validation
    known_dead_python = {"unused_function", "_private_unused", "UnusedClass", "UNUSED_CONSTANT"}
    known_dead_ts = {"unusedInternalFunction", "UnusedHelper", "UNUSED_SECRET", "UnusedType"}

    print("\n" + "="*60)
    print(" TREE-SITTER DEAD CODE DETECTION TEST")
    print("="*60)
    print("\nKnown dead code:")
    print(f"  Python: {known_dead_python}")
    print(f"  TypeScript: {known_dead_ts}")

    # Single file analysis
    py_main = str(base_dir / "sample_python.py")
    ts_main = str(base_dir / "sample_typescript.ts")

    py_results = detector.analyze_single_file(py_main)
    ts_results = detector.analyze_single_file(ts_main)

    print_analysis_results(py_results, "Python Single File Analysis")
    print_analysis_results(ts_results, "TypeScript Single File Analysis")

    # Cross-file analysis
    all_files = [
        str(base_dir / "sample_python.py"),
        str(base_dir / "consumer_python.py"),
        str(base_dir / "sample_typescript.ts"),
        str(base_dir / "consumer_typescript.ts"),
    ]

    project_results = detector.analyze_project(all_files)
    print_project_results(project_results)

    # Validation
    print("\n" + "="*60)
    print(" VALIDATION RESULTS")
    print("="*60)

    detected_dead = set()
    for item in project_results.get("exported_but_unused", []):
        detected_dead.add(item["name"])
    for item in project_results.get("private_unused", []):
        detected_dead.add(item["name"])
    for items in project_results.get("single_file_dead_code", {}).values():
        for item in items:
            detected_dead.add(item["name"])

    all_known_dead = known_dead_python | known_dead_ts

    # True positives
    true_positives = detected_dead & all_known_dead
    print(f"\n[True Positives] (correctly detected as dead)")
    for name in sorted(true_positives):
        print(f"  + {name}")

    # False negatives
    false_negatives = all_known_dead - detected_dead
    print(f"\n[False Negatives] (missed dead code)")
    for name in sorted(false_negatives):
        print(f"  - {name}")

    # False positives
    false_positives = detected_dead - all_known_dead
    print(f"\n[False Positives] (flagged but actually used)")
    for name in sorted(false_positives):
        print(f"  ! {name}")

    # Summary
    print("\n" + "="*60)
    print(" ANALYSIS SUMMARY")
    print("="*60)
    print(f"\nDetection accuracy:")
    print(f"  True positives:  {len(true_positives)}/{len(all_known_dead)}")
    print(f"  False negatives: {len(false_negatives)}")
    print(f"  False positives: {len(false_positives)}")

    print("\n[Limitations of this approach]")
    limitations = [
        "1. Dynamic calls (getattr, eval, reflection) not detected",
        "2. __all__ exports in Python not handled",
        "3. String-based imports not tracked",
        "4. Decorator usage patterns may be missed",
        "5. Entry points (main, __main__) need special handling",
        "6. Framework callbacks (Flask routes, pytest fixtures) appear unused",
        "7. Type-only imports in TypeScript may need special handling",
        "8. Re-exports (export * from) not fully tracked",
        "9. No scope analysis - name shadowing causes false positives",
        "10. Magic methods (__init__, __str__) flagged incorrectly",
    ]
    for lim in limitations:
        print(f"  {lim}")

    print("\n[Assessment: Is universal dead code detection feasible?]")
    print("""
  Tree-sitter provides excellent AST extraction, but dead code detection
  requires more than syntax analysis:

  FEASIBLE with tree-sitter:
  - Basic definition/reference extraction
  - Static import/export tracking
  - Simple unused local variable detection
  - Convention-based private symbol detection

  REQUIRES ADDITIONAL WORK:
  - Full scope/binding analysis (not built into tree-sitter)
  - Type information for method resolution
  - Framework-specific entry point knowledge
  - Dynamic language escape hatches (eval, getattr, etc.)
  - Cross-file module resolution
  - Namespace/alias tracking

  VERDICT: A production-quality tool is possible but requires:
  - Significant additional logic beyond tree-sitter parsing
  - Language-specific heuristics and special cases
  - Configurable entry points and export patterns
  - Integration with type checkers (mypy, TypeScript) for accuracy
  - False positive suppression mechanisms (comments, config)

  RECOMMENDATION: Tree-sitter is a good foundation, but consider:
  - Python: pylint, vulture, or pyflakes for better coverage
  - TypeScript: ESLint with typescript-eslint, or knip
  - These tools handle edge cases tree-sitter alone cannot
""")


if __name__ == "__main__":
    main()
