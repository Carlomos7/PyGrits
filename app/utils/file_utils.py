"""
file_utils.py: File operation utilities for the version control system.
"""

from pathlib import Path
from typing import Optional

def ensure_dir(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path (Path): Directory path to ensure
    """
    path.mkdir(parents=True, exist_ok=True)

def get_relative_path(file_path: Path, base_path: Path) -> str:
    """Get relative path from base path.

    Args:
        file_path (Path): File path to convert
        base_path (Path): Base path to relate to

    Returns:
        str: Relative path
    """
    return str(file_path.resolve().relative_to(base_path))

def write_text_file(path: Path, content: str) -> None:
    """Write content to a text file, creating directories if needed.

    Args:
        path (Path): Path to write to
        content (str): Content to write
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def read_text_file(path: Path) -> Optional[str]:
    """Read content from a text file.

    Args:
        path (Path): Path to read from

    Returns:
        Optional[str]: File content if successful, None otherwise
    """
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        return None