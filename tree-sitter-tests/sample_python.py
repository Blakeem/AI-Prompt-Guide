"""Sample Python file for tree-sitter testing.

This file contains various code patterns to test:
- Functions and classes
- Complexity patterns
- Potentially dead code
- Imports
"""
import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass


# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
UNUSED_CONSTANT = "never_used"  # Dead code candidate


@dataclass
class Config:
    """Configuration dataclass."""
    host: str
    port: int
    debug: bool = False


class DatabaseConnection:
    """Database connection handler."""

    def __init__(self, config: Config):
        self.config = config
        self.connection = None
        self._is_connected = False

    def connect(self) -> bool:
        """Establish database connection."""
        if self._is_connected:
            return True

        try:
            # Simulated connection
            self.connection = f"conn://{self.config.host}:{self.config.port}"
            self._is_connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def disconnect(self):
        """Close connection."""
        self.connection = None
        self._is_connected = False

    def _internal_helper(self):
        """Private method - potential dead code."""
        pass

    def execute_query(self, query: str) -> Optional[List[Dict]]:
        """Execute a database query with retry logic."""
        if not self._is_connected:
            if not self.connect():
                return None

        # Complex nested logic for complexity testing
        results = []
        for attempt in range(MAX_RETRIES):
            try:
                if self.config.debug:
                    if len(query) > 100:
                        if "SELECT" in query:
                            print(f"Long SELECT query on attempt {attempt}")
                        else:
                            print(f"Long non-SELECT query")
                    else:
                        print(f"Short query")

                # Simulate query execution
                for i in range(10):
                    if i % 2 == 0:
                        for j in range(5):
                            if j > 2:
                                results.append({"id": i, "value": j})

                return results
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                continue

        return None


def simple_function(x: int) -> int:
    """Simple function with low complexity."""
    return x * 2


def medium_complexity_function(data: List[int]) -> List[int]:
    """Function with medium complexity."""
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
        elif item < 0:
            result.append(item * -1)
        else:
            result.append(0)
    return result


def high_complexity_function(data: Dict, flags: Dict) -> Dict:
    """Function with high complexity - code smell."""
    result = {}

    for key, value in data.items():
        if key.startswith("a"):
            if value > 100:
                if flags.get("transform"):
                    if flags.get("uppercase"):
                        result[key.upper()] = value * 2
                    else:
                        result[key] = value * 2
                else:
                    result[key] = value
            elif value > 50:
                result[key] = value + 10
            else:
                result[key] = value
        elif key.startswith("b"):
            if isinstance(value, list):
                for item in value:
                    if item > 0:
                        result[f"{key}_{item}"] = item
        else:
            result[key] = value

    return result


def unused_function():
    """This function is never called - dead code."""
    return "I am never used"


def _private_unused():
    """Private unused function."""
    return None


class UnusedClass:
    """This class is never instantiated - dead code candidate."""

    def method_one(self):
        pass

    def method_two(self):
        pass


def function_with_many_params(a, b, c, d, e, f, g, h):
    """Code smell: too many parameters."""
    return a + b + c + d + e + f + g + h


# Module-level code
def main():
    """Main entry point."""
    config = Config(host="localhost", port=5432, debug=True)
    db = DatabaseConnection(config)

    result = db.execute_query("SELECT * FROM users")
    simple_function(5)
    medium_complexity_function([1, -2, 0, 3])

    return result


if __name__ == "__main__":
    main()
