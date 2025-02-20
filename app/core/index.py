"""
index.py: Manages the staging area functionality.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from app.utils.logger import logger
from app.utils.file_utils import get_relative_path, read_text_file, write_text_file


class Index:
    def __init__(self, index_path: Path):
        """Initialize index manager.

        Args:
            index_path (Path): Path to the index file
        """
        self.index_path = index_path

    def read(self) -> Dict[str, Any]:
        """Read the current index state.

        Returns:
            Dict[str, Any]: Current index contents
        """
        try:
            content = read_text_file(self.index_path)
            if content:
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.debug(f"Creating new index due to: {str(e)}")

        return {"version": 1, "entries": {}}

    def write(self, index_data: Dict[str, Any]) -> None:
        """Write index data to file.

        Args:
            index_data (Dict[str, Any]): Index data to write
        """
        try:
            content = json.dumps(index_data, indent=2)
            write_text_file(self.index_path, content)
        except Exception as e:
            logger.error(f"Failed to write index: {str(e)}")
            raise

    def add_file(self, file_path: Path, hash_value: str, repo_path: Path) -> None:
        """Add a file to the index.

        Args:
            file_path (Path): Path to the file being added
            hash_value (str): Hash of the file content
            repo_path (Path): Repository root path for relative path calculation
        """
        try:
            index = self.read()
            rel_path = get_relative_path(file_path, repo_path)

            # Update file entry
            index["entries"][rel_path] = {
                "hash": hash_value,
                "timestamp": datetime.now().isoformat(),
                "size": file_path.stat().st_size,
            }

            self.write(index)
            logger.debug(f"Added to index: {rel_path}")

        except Exception as e:
            logger.error(f"Failed to add file to index: {str(e)}")
            raise

    def get_staged_files(self) -> Dict[str, Any]:
        """Get all staged files.

        Returns:
            Dict[str, Any]: Dictionary of staged files and their information
        """
        return self.read().get("entries", {})

    def is_staged(self, file_path: Path, repo_path: Path) -> bool:
        """Check if a file is staged.

        Args:
            file_path (Path): Path to check
            repo_path (Path): Repository root path

        Returns:
            bool: True if file is staged
        """
        rel_path = get_relative_path(file_path, repo_path)
        return rel_path in self.get_staged_files()

    def clear(self) -> None:
        """Clear the staging area."""
        self.write({"version": 1, "entries": {}})
