import os
from pathlib import Path
import hashlib
import json
from typing import Dict, Any
from datetime import datetime


class Repository:

    def __init__(self, path: str = "."):
        """Initialize a new repository object.

        Args:
            path (str, optional): Path to the repository. Defaults to ".".
        """

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
        """Check if the repository is initialized.

        Returns:
            bool: True if the repository is initialized, False otherwise.
        """
        return (
            self.vcs_dir.exists()
            and self.objects_dir.exists()
            and self.head_file.exists()
        )

    def init(self):
        """Initialize a new repository.
        Creates the version control directory structure and initial files.
        """

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

    def hash_object(self, data: bytes) -> str:
        """Hash the provided data using SHA1.

        Args:
            data (str): Data to be hashed
        """

        hasher = hashlib.sha1()
        hasher.update(data.encode("utf-8"))
        hash_value = hasher.hexdigest()

        return hash_value

    def _update_index(self, file_path: Path, hash_value: str) -> None:
        """Update the index file with the new file entry.

        Args:
            file_path (Path): Path to the file to be added
            hash_value (str): Hash value of the file contents
        """
        # Read the contents of the index file and do a json parse on it
        # Then add the new file to the index and write it back to the index file

        # Get relative path from repository root for storage
        rel_path = str(file_path.relative_to(self.path))

        try:
            with open(self.index_file, "r") as f:  # Read the index file
                index = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # If index is corrupted or missing, create new
            index = {"version": 1, "entries": {}}

        # Update file entry
        index["entries"][rel_path] = {  # Add the file to the index
            "hash": hash_value,
            "timestamp": datetime.now().isoformat(),
            "size": file_path.stat().st_size,
        }

        # Write the updated index back to the index file
        with open(self.index_file, "w") as f:
            json.dump(index, f, indent=2)

    def add(self, file_path: str) -> None:
        """Add a file to the repository.

        Args:
            file_path (str): Path to the file to be added
        """

        if not self._initialized:
            raise ValueError("Repository not initialized")

        # Convert the provided path to a Path object for better manipulation
        file_path = Path(file_path).resolve()

        # Validation checks
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")

        if not str(file_path).startswith(str(self.path)):
            raise ValueError("File is outside repository")

        # Read the file and hash contents
        file_contents = file_path.read_text(encoding="utf-8")
        file_hash = self.hash_object(file_contents)

        print(f"Hash: {file_hash}")

        # Write the file contents to the objects directory
        object_path = self.objects_dir / file_hash
        object_path.write_text(file_contents, encoding="utf-8")

        self._update_index(file_path, file_hash)
        print(f"File to be added: {file_path}")

    def get_head(self) -> str:
        """Get the current HEAD commit hash.

        Returns:
            str: HEAD commit hash
        """
        if not self._initialized:
            raise ValueError("Repository not initialized")

        try:
            return self.head_file.read_text().strip()
        except FileNotFoundError:
            return ""

    def set_head(self, commit_hash: str) -> None:
        """
        Set the current HEAD commit hash.

        Args:
            commit_hash (str): Commit hash to be set as HEAD
        """
        self.head_file.write_text(commit_hash)

    def get_staged_files(self) -> Dict[str, Any]:
        """Get the list of staged files.

        Returns:
            Dict[str, Any]: Dictionary of staged files
        """
        try:
            with open(self.index_file, "r") as f:
                index = json.load(f)
                return index["entries"]
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def create_commit(self, message: str) -> str:
        """Create a new commit with staged changes.

        Args:
            message (str): Commit message

        Returns:
            str: Hash of the new commit

        Raises:
            ValueError: If repository isn't initialized, no files are staged,
                    or commit message is invalid
        """
        if not self._initialized:
            raise ValueError("Repository not initialized")

        if not message or not message.strip():
            raise ValueError("Commit message cannot be empty")

        # Get staged files
        staged_files = self.get_staged_files()
        if not staged_files:
            raise ValueError("No files staged for commit")

        # Create commit object with additional metadata
        commit_data = {
            "parent": self.get_head(),
            "timestamp": datetime.now().isoformat(),
            "message": message.strip(),
            "files": staged_files,
            "author": os.environ.get("USER", "unknown"),  # Add author information
        }

        try:
            # Convert commit data to string and hash it
            commit_content = json.dumps(commit_data, indent=2, sort_keys=True)
            commit_hash = self.hash_object(commit_content)

            # Store commit object
            commit_path = self.objects_dir / commit_hash
            commit_path.write_text(commit_content, encoding="utf-8")

            # Update HEAD to point to the new commit
            self.set_head(commit_hash)

            # Clear the staging area
            with open(self.index_file, "w") as f:
                json.dump({"version": 1, "entries": {}}, f, indent=2)

            print(f"Created commit {commit_hash[:8]}")  # Show shortened hash
            print(f"Message: {message}")
            return commit_hash

        except Exception as e:
            raise RuntimeError(f"Failed to create commit: {str(e)}")

    def get_commit(self, commit_hash: str) -> Dict[str, Any]:
        """Get the commit object for the provided commit hash.

        Args:
            commit_hash (str): Commit hash

        Returns:
            Dict[str, Any]: Commit object
        """
        commit_path = self.objects_dir / commit_hash

        if not commit_path.exists():
            raise ValueError(f"Commit {commit_hash} not found")
        try:
            commit_content = commit_path.read_text("utf-8")
            return json.loads(commit_content)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError(f"Invalid commit object {commit_hash}")

    def log(self, max_entries: int = None) -> None:
        """Display commit history.

        Args:
            max_entries (int, optional): Maximum number of entries to display. Defaults to None.
        """
        current_commit = self.get_head()
        count = 0

        while current_commit and (max_entries is None or count < max_entries):
            try:
                commit_data = self.get_commit(current_commit)
                print(f"Commit: {current_commit}")
                print(f"Date: {commit_data['timestamp']}")
                print(f"Message: {commit_data['message']}")
                print("-" * 50)

                current_commit = commit_data.get("parent", "")
                count += 1

            except ValueError:
                print(f"Invalid commit {current_commit}")
                break


if __name__ == "__main__":
    # Simmple command line interface to init and add a file to the repository
    repo = Repository()
    # repo.init()
    repo.add("sample.txt")
    repo.create_commit("Third commit")
    repo.log()
