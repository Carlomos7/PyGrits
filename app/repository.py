import os
from pathlib import Path
import hashlib
import json
from typing import Dict, Any
from datetime import datetime


class Repository:

    def __init__(self, path: str = "."):

        self.path = Path(
            path
        ).resolve()  # Convert the provided path to a Path object for better manipulation

        # Define the main directory path
        self.vcs_dir = self.path / ".pygrits"

        # Define paths for internal storage structures
        self.objects_dir = self.vcs_dir / "objects"

        # Define paths for control files
        self.head_file = self.vcs_dir / "HEAD"
        self.index_file = self.vcs_dir / "index"

        # Internal state tracking
        self._initialized = self._check_initialized()

    def _check_initialized(self) -> bool:
        return (
            self.vcs_dir.exists()
            and self.objects_dir.exists()
            and self.head_file.exists()
        )

    def init(self):
        if self._initialized:
            raise Exception("Repository already initialized")

        # Create directory structure
        self.objects_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.head_file.touch(exist_ok=False)
            # Initialize empty index file with JSON structure
            with open(self.index_file, "w") as f:
                json.dump({"version": 1, "entries": {}}, f, indent=2)
        except FileExistsError:
            raise Exception("Repository already initialized")

        # Mark repository as initialized
        self._initialized = True

        print(f"Initialized empty repository in {self.path}")