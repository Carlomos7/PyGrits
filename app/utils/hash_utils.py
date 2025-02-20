"""
hash_utils.py: Provides hashing functionality for the version control system.
"""

import hashlib
from pathlib import Path
from typing import Tuple

def hash_object(data: str) -> str:
    """Hash the provided data using SHA1.

    Args:
        data (str): Data to be hashed

    Returns:
        str: SHA1 hash of the data
    """
    hasher = hashlib.sha1()
    hasher.update(data.encode("utf-8"))
    return hasher.hexdigest()

def hash_file(file_path: Path) -> Tuple[str, str]:
    """Hash the contents of a file.

    Args:
        file_path (Path): Path to the file

    Returns:
        Tuple[str, str]: (hash, content) of the file
    """
    content = file_path.read_text(encoding="utf-8")
    return hash_object(content), content