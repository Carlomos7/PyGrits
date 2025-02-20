"""
objects.py: Core object storage and retrieval functionality.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from ..utils.hash_utils import hash_object
from ..utils.file_utils import write_text_file, read_text_file
from ..utils.logger import logger


class ObjectStore:
    def __init__(self, objects_dir: Path):
        self.objects_dir = objects_dir

    def store_object(self, content: str) -> str:
        """Store content and return its hash.

        Args:
            content (str): Content to store

        Returns:
            str: Hash of the stored content
        """
        hash_value = hash_object(content)
        object_path = self.objects_dir / hash_value

        if not object_path.exists():
            write_text_file(object_path, content)

        return hash_value

    def get_object(self, hash_value: str) -> Optional[str]:
        """Retrieve content by its hash.

        Args:
            hash_value (str): Hash of the content

        Returns:
            Optional[str]: Content if found, None otherwise
        """
        object_path = self.objects_dir / hash_value
        return read_text_file(object_path)

    def create_commit(
        self, message: str, files: Dict[str, Any], parent: str = ""
    ) -> str:
        """Create a commit object.

        Args:
            message (str): Commit message
            files (Dict[str, Any]): Staged files information
            parent (str, optional): Parent commit hash. Defaults to "".

        Returns:
            str: Hash of the new commit
        """
        commit_data = {
            "parent": parent,
            "timestamp": datetime.now().isoformat(),
            "message": message.strip(),
            "files": files,
        }

        commit_content = json.dumps(commit_data, indent=2, sort_keys=True)
        return self.store_object(commit_content)

    def get_commit(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Get commit data by hash.

        Args:
            commit_hash (str): Commit hash

        Returns:
            Optional[Dict[str, Any]]: Commit data if found, None otherwise
        """
        content = self.get_object(commit_hash)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error(f"Invalid commit format: {commit_hash}")
        return None
