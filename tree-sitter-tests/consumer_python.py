"""Consumer module to test cross-file reference detection."""

from sample_python import (
    Config,
    DatabaseConnection,
    simple_function,
    medium_complexity_function,
    MAX_RETRIES,
)
# Note: unused_function, UnusedClass, high_complexity_function NOT imported


def use_imports():
    """Uses some of the imported symbols."""
    config = Config(host="127.0.0.1", port=5432)
    db = DatabaseConnection(config)

    result = simple_function(10)
    transformed = medium_complexity_function([1, 2, 3])

    for _ in range(MAX_RETRIES):
        db.connect()

    return result, transformed
