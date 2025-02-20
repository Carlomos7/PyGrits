"""
repository.py: Main repository management class for PyGrits.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import difflib
from colorama import Fore, Style

from utils.logger import logger
from utils.file_utils import ensure_dir, get_relative_path
from utils.hash_utils import hash_file
from objects import ObjectStore
from index import Index

class Repository:
    def __init__(self, path: str = "."):
        """Initialize a new repository object.

        Args:
            path (str, optional): Path to the repository. Defaults to ".".
        """
        self.path = Path(path).resolve()
        self.vcs_dir = self.path / ".pygrits"
        self.objects_dir = self.vcs_dir / "objects"
        self.head_file = self.vcs_dir / "HEAD"
        self.index_file = self.vcs_dir / "index"

        # Initialize components
        self.object_store = ObjectStore(self.objects_dir)
        self.index = Index(self.index_file)

        # Internal state tracking
        self._initialized = self._check_initialized()

        # Set up logging file
        self.log_file = self.vcs_dir / "pygrits.log"
        if self._initialized and not self.log_file.parent.exists():
            ensure_dir(self.log_file.parent)

    def _check_initialized(self) -> bool:
        """Check if the repository is initialized."""
        return (
            self.vcs_dir.exists()
            and self.objects_dir.exists()
            and self.head_file.exists()
        )

    def init(self) -> None:
        """Initialize a new repository."""
        if self._initialized:
            logger.error("Repository already initialized")
            raise ValueError("Repository already initialized")

        try:
            # Create directory structure
            ensure_dir(self.objects_dir)
            self.head_file.touch(exist_ok=False)

            # Initialize empty index
            self.index.clear()

            self._initialized = True
            logger.info(f"Initialized repository at {self.path}")

        except Exception as e:
            logger.error(f"Failed to initialize repository: {str(e)}")
            raise

    def add(self, file_path: str) -> None:
        """Add a file to the staging area."""
        if not self._initialized:
            logger.error("Repository not initialized")
            raise ValueError("Repository not initialized")

        try:
            file_path = Path(file_path).resolve()

            # Validation checks
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")

            if not str(file_path).startswith(str(self.path)):
                logger.error("File is outside repository")
                raise ValueError("File is outside repository")

            # Hash file and store content
            file_hash, content = hash_file(file_path)
            self.object_store.store_object(content)

            # Update index
            self.index.add_file(file_path, file_hash, self.path)

            logger.info(f"Added file: {file_path.relative_to(self.path)}")
            logger.debug(f"File hash: {file_hash}")

        except Exception as e:
            logger.error(f"Failed to add file: {str(e)}")
            raise

    def get_head(self) -> str:
        """Get the current HEAD commit hash."""
        if not self._initialized:
            logger.error("Repository not initialized")
            raise ValueError("Repository not initialized")

        try:
            return self.head_file.read_text().strip()
        except FileNotFoundError:
            return ""

    def set_head(self, commit_hash: str) -> None:
        """Set the current HEAD commit hash."""
        self.head_file.write_text(commit_hash)

    def create_commit(self, message: str) -> str:
        """Create a new commit with staged changes."""
        if not self._initialized:
            logger.error("Repository not initialized")
            raise ValueError("Repository not initialized")

        if not message or not message.strip():
            logger.error("Commit message cannot be empty")
            raise ValueError("Commit message cannot be empty")

        try:
            # Get staged files and create commit
            staged_files = self.index.get_staged_files()
            if not staged_files:
                logger.warning("No files staged for commit")
                raise ValueError("No files staged for commit")

            commit_hash = self.object_store.create_commit(
                message=message, files=staged_files, parent=self.get_head()
            )

            # Update HEAD and clear staging
            self.set_head(commit_hash)
            self.index.clear()

            logger.info(f"Created commit: {commit_hash[:8]}")
            logger.debug(f"Full commit hash: {commit_hash}")
            return commit_hash

        except Exception as e:
            logger.error(f"Failed to create commit: {str(e)}")
            raise

    def log(self, max_entries: int = None) -> None:
        """Display commit history."""
        if not self._initialized:
            logger.error("Repository not initialized")
            raise ValueError("Repository not initialized")

        current_commit = self.get_head()
        if not current_commit:
            logger.info("No commits yet")
            return

        count = 0
        while current_commit and (max_entries is None or count < max_entries):
            try:
                commit_data = self.object_store.get_commit(current_commit)
                if not commit_data:
                    break

                logger.info(
                    f"{Fore.YELLOW}Commit: {current_commit}{Style.RESET_ALL}\n"
                    f"Date: {commit_data['timestamp']}\n"
                    f"Message: {commit_data['message']}\n"
                    f"{'-' * 50}"
                )

                current_commit = commit_data.get("parent", "")
                count += 1

            except Exception as e:
                logger.error(f"Error reading commit {current_commit}: {str(e)}")
                break

    def show_commit_diff(self, commit_hash: str) -> None:
        """Show changes introduced by a commit."""
        try:
            commit_data = self.object_store.get_commit(commit_hash)
            if not commit_data:
                logger.error(f"Commit {commit_hash} not found")
                return

            parent_hash = commit_data.get("parent", "")

            logger.info(
                f"\n{Fore.YELLOW}Commit: {commit_hash}{Style.RESET_ALL}\n"
                f"Date: {commit_data['timestamp']}\n"
                f"Message: {commit_data['message']}\n"
            )

            changed_files = commit_data.get("files", {})
            for file_path in changed_files:
                current_content = self.object_store.get_object(
                    changed_files[file_path]["hash"]
                )

                # Get parent content if available
                parent_content = ""
                if parent_hash:
                    parent_commit = self.object_store.get_commit(parent_hash)
                    if parent_commit and file_path in parent_commit["files"]:
                        parent_content = self.object_store.get_object(
                            parent_commit["files"][file_path]["hash"]
                        )

                self._show_file_diff(file_path, parent_content, current_content)

        except Exception as e:
            logger.error(f"Error showing diff: {str(e)}")
            raise

    def _show_file_diff(
        self, file_path: str, old_content: str, new_content: str
    ) -> None:
        """Show diff for a single file."""
        if not old_content:
            logger.info(f"\n{Fore.CYAN}New file: {file_path}{Style.RESET_ALL}")
            for line in new_content.splitlines():
                logger.info(f"{Fore.GREEN}+ {line}{Style.RESET_ALL}")
            return

        diff = list(
            difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm="",
            )
        )

        if diff:
            logger.info(f"\n{Fore.CYAN}Modified: {file_path}{Style.RESET_ALL}")
            for line in diff:
                if line.startswith("+"):
                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                elif line.startswith("-"):
                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                elif line.startswith("@"):
                    print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                else:
                    print(line)

if __name__ == "__main__":
    repo = Repository()

    repo.add("app/repository.py")
    repo.add("app/index.py")
    commit_hash = repo.create_commit("Initial commit")
    repo.log()
    repo.show_commit_diff(commit_hash)